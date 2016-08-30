#!/usr/bin/env python2
import libtorrent as lt
import sys
import os
import hashlib
import math
torrents_dir="/mnt/code2/torrents"
def get_name(filename):
    torrent_file=filename
    if not os.access(torrent_file,os.R_OK):
        print("Files not accesible")
    with open(torrent_file,"rb") as f:
        data=f.read()
    torrent_data=lt.bdecode(data)
    torrent_info=torrent_data[b'info']
    return torrent_info[b'name']

def change_name(filename):
    newfilename=os.path.dirname(filename) + "/" + get_name(filename) + ".torrent"
    print(filename + " -> " + newfilename)
    os.rename(filename,newfilename)

def check_one_file(filename, filelength, piece_length, pieces):
    print("filename: " + filename + " size: " + str(filelength))
    print("checking size")
    assert os.stat(filename).st_size==filelength
    print(str(os.stat(filename).st_size) + " == " + str(filelength))
    print("piece length: " + str(piece_length))
    pieces_num=filelength/piece_length + (0,1)[int(filelength%piece_length!=0)]
    hashes_num=len(pieces)/20 
    if len(pieces)%20!=0:
        print("pieces length invalid")
    assert pieces_num==hashes_num
    print("pieces check: " + str(pieces_num) + " == " + str(hashes_num))
    wrong_pieces=[]
    with open(filename,"rb") as fhandle:
        for i in range(hashes_num):
            data=fhandle.read(piece_length)
            sha1_handle=hashlib.sha1(data)
            sha1_from_data=sha1_handle.digest()
            sha1_from_piece=pieces[i*20:i*20+20]
            if sha1_from_data==sha1_from_piece:
                sys.stdout.write("+")
            else:
                sys.stdout.write("-")
                wrong_pieces.append(i)
    print("")
    return len(wrong_pieces)==0,wrong_pieces

def check_directory(directory, files, piece_length, pieces):
    os.chdir(directory)
    fhandle_list=[]
    total_size=0
    for item in files:
        filepath="/".join(item["path"])
        fhandle=open(filepath, "rb")
        fhandle_list.append(fhandle)
        fsize=os.stat(filepath).st_size
        assert fsize==item["length"]
        print("checking size: " + str(fsize) + " == " + str(item["length"]))
        total_size+=item["length"]
    pieces_num=total_size/piece_length + (0,1)[int(total_size%piece_length!=0)]
    hashes_num=len(pieces)/20
    if len(pieces)%20!=0:
        print("pieces length invalid")
    assert pieces_num == hashes_num
    print("pieces check: " + str(pieces_num) + " == " + str(hashes_num))
    file_index=0
    print("file " + "/".join(files[file_index]["path"]))
    wrong_pieces=[]
    for i in range(hashes_num):
        data=fhandle_list[file_index].read(piece_length)
        while len(data)<piece_length and file_index<(len(fhandle_list)-1):
            file_index+=1
            print("\n file " + "/".join(files[file_index]["path"]))
            added_data=fhandle_list[file_index].read(piece_length-len(data))
            data+=added_data
        sha1_from_data=hashlib.sha1(data).digest()
        sha1_from_piece=pieces[i*20:i*20+20]
        if sha1_from_data==sha1_from_piece:
            sys.stdout.write("+")
        else:
            sys.stdout.write("-")
            wrong_pieces.append(i)
    return len(wrong_pieces)==0,wrong_pieces


def check(torrent_file, checking_file):
    if not os.access(torrent_file,os.R_OK) or not os.access(checking_file,os.R_OK):
        print("Files not accesible")
    with open(torrent_file,"rb") as f:
        data=f.read()
    torrent_data=lt.bdecode(data)
    torrent_info=torrent_data[b'info']
    if b'length' in torrent_info:
        return check_one_file(checking_file, int(torrent_info[b'length']),
                int(torrent_info[b'piece length']),torrent_info[b'pieces'])
    elif b'files' in torrent_info:
        return check_directory(checking_file, torrent_info[b'files'],
                int(torrent_info[b'piece length']),torrent_info[b'pieces'])


def test1():
    print("checking one file")
    torrent_file="/mnt/code2/torrents/1aaa5f604c8d3d59edfd368a8c0e573090ab7e8b.torrent"
    checking_file="/mnt/code2/down/Automotive Embedded Systems Handbook (2008)BBS.pdf"
    print(check(torrent_file, checking_file))

def test2():
    print("checking multiple files")
    torrent_file="/mnt/code2/torrents/8c01288476f9b4fb43722e48dc77f28ef6413b2c.torrent"
    checking_file="/mnt/code2/down/EasyBCD 2.2.0.182"
    print(check(torrent_file, checking_file))

def main():
    if len(sys.argv)>2:
        if sys.argv[1]=="change":
            change_name(sys.argv[2])
        elif sys.argv[1]=="check":
            basename=os.path.basename(sys.argv[2])
            torrent_file=torrents_dir + "/" + basename + ".torrent"
            print("Searching " + torrent_file)
            if not os.access(torrent_file, os.R_OK):
                print("no torrent found")
                return
            print(check(torrent_file, sys.argv[2]))
    elif len(sys.argv)>3 and sys.argv[1]=="checkfile":
        print(check(sys.argv[2],sys.argv[3]))
    

if __name__ == "__main__":
    main()
