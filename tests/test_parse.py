import pytest
import subprocess
import os
import sys
import struct

prefix = 'src/pycdlib'
for i in range(0,3):
    if os.path.exists(os.path.join(prefix, 'pycdlib.py')):
        sys.path.insert(0, prefix)
        break
    else:
        prefix = '../' + prefix

import pycdlib

from common import *

def do_a_test(tmpdir, outfile, check_func):
    testout = tmpdir.join("writetest.iso")

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()
    iso.open(str(outfile))
    check_func(iso, os.stat(str(outfile)).st_size)

    iso.write(str(testout))

    iso.close()

    # Now round-trip through write.
    iso2 = pycdlib.PyIso()
    iso2.open(str(testout))
    check_func(iso2, os.stat(str(outfile)).st_size)
    iso2.close()

def test_parse_invalid_file(tmpdir):
    iso = pycdlib.PyIso()
    with pytest.raises(TypeError):
        iso.open(None)

def test_parse_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("nofiles")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_nofiles)

def test_parse_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_onefile)

def test_parse_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("onedir")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_onedir)

def test_parse_twofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    with open(os.path.join(str(indir), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_twofiles)

def test_parse_twodirs(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("onefileonedir")
    outfile = str(indir)+".iso"
    indir.mkdir("bb")
    indir.mkdir("aa")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_twodirs)

def test_parse_onefileonedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("onefileonedir")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_onefileonedir)

def test_parse_onefile_onedirwithfile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("onefileonedirwithfile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(dir1), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_onefile_onedirwithfile)

def test_parse_tendirs(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("tendirs")
    outfile = str(indir)+".iso"
    numdirs = 10
    for i in range(1, 1+numdirs):
        indir.mkdir("dir%d" % i)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_tendirs)

def test_parse_dirs_overflow_ptr_extent(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("manydirs")
    outfile = str(indir)+".iso"
    numdirs = 295
    for i in range(1, 1+numdirs):
        indir.mkdir("dir%d" % i)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_dirs_overflow_ptr_extent)

def test_parse_dirs_just_short_ptr_extent(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("manydirs")
    outfile = str(indir)+".iso"
    numdirs = 293
    for i in range(1, 1+numdirs):
        indir.mkdir("dir%d" % i)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_dirs_just_short_ptr_extent)

def test_parse_twoextentfile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("bigfile")
    outfile = str(indir)+".iso"
    outstr = ""
    for j in range(0, 8):
        for i in range(0, 256):
            outstr += struct.pack("=B", i)
    outstr += struct.pack("=B", 0)
    with open(os.path.join(str(indir), "bigfile"), 'wb') as outfp:
        outfp.write(outstr)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    testout = tmpdir.join("writetest.iso")

    do_a_test(tmpdir, outfile, check_twoextentfile)

def test_parse_twoleveldeepdir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twoleveldeep")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    dir1.mkdir("subdir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_twoleveldeepdir)

def test_parse_twoleveldeepfile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twoleveldeepfile")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    subdir1 = dir1.mkdir("subdir1")
    with open(os.path.join(str(subdir1), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_twoleveldeepfile)

def test_parse_joliet_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("joliet")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_nofiles)

def test_parse_joliet_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("joliet")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_onedir)

def test_parse_joliet_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietfile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_onefile)

def test_parse_joliet_onefileonedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietfile")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_onefileonedir)

def test_parse_eltorito_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_nofiles)

def test_parse_eltorito_twofile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritotwofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "aa"), 'wb') as outfp:
        outfp.write("aa\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_twofile)

def test_parse_rr_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrnofiles")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_nofiles)

def test_parse_rr_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rronefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_onefile)

def test_parse_rr_twofile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrtwofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    with open(os.path.join(str(indir), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_twofile)

def test_parse_rr_onefileonedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rronefileonedir")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_onefileonedir)

def test_parse_rr_onefileonedirwithfile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rronefileonedirwithfile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(dir1), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_onefileonedirwithfile)

def test_parse_rr_symlink(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlink")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("foo", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_symlink)

def test_parse_rr_symlink2(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlink2")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(dir1), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("dir1/foo", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_symlink2)

def test_parse_rr_symlink_dot(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlinkdot")
    outfile = str(indir)+".iso"
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink(".", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_symlink_dot)

def test_parse_rr_symlink_dotdot(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlinkdotdot")
    outfile = str(indir)+".iso"
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("..", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_symlink_dotdot)

def test_parse_rr_symlink_broken(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlinkbroken")
    outfile = str(indir)+".iso"
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("foo", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_symlink_broken)

def test_parse_alternating_subdir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("alternating")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "bb"), 'wb') as outfp:
        outfp.write("bb\n")
    cc = indir.mkdir("cc")
    aa = indir.mkdir("aa")
    with open(os.path.join(str(indir), "dd"), 'wb') as outfp:
        outfp.write("dd\n")
    with open(os.path.join(str(cc), "sub2"), 'wb') as outfp:
        outfp.write("sub2\n")
    with open(os.path.join(str(aa), "sub1"), 'wb') as outfp:
        outfp.write("sub1\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_alternating_subdir)

def test_parse_rr_verylongname(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrverylongname")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "a"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("aa\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_verylongname)

def test_parse_rr_verylongname_joliet(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrverylongname")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "a"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("aa\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_verylongname_joliet)

def test_parse_rr_manylongname(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrmanylongname")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "a"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("aa\n")
    with open(os.path.join(str(indir), "b"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("bb\n")
    with open(os.path.join(str(indir), "c"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("cc\n")
    with open(os.path.join(str(indir), "d"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("dd\n")
    with open(os.path.join(str(indir), "e"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("ee\n")
    with open(os.path.join(str(indir), "f"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("ff\n")
    with open(os.path.join(str(indir), "g"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("gg\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_manylongname)

def test_parse_rr_manylongname2(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrmanylongname2")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "a"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("aa\n")
    with open(os.path.join(str(indir), "b"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("bb\n")
    with open(os.path.join(str(indir), "c"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("cc\n")
    with open(os.path.join(str(indir), "d"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("dd\n")
    with open(os.path.join(str(indir), "e"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("ee\n")
    with open(os.path.join(str(indir), "f"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("ff\n")
    with open(os.path.join(str(indir), "g"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("gg\n")
    with open(os.path.join(str(indir), "h"*RR_MAX_FILENAME_LENGTH), 'wb') as outfp:
        outfp.write("hh\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_manylongname2)

def test_parse_joliet_and_rr_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandrrnofiles")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_rr_nofiles)

def test_parse_joliet_and_rr_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandrronefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_rr_onefile)

def test_parse_joliet_and_rr_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandrronedir")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_rr_onedir)

def test_parse_rr_and_eltorito_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrandeltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_and_eltorito_nofiles)

def test_parse_rr_and_eltorito_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrandeltoritoonefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_and_eltorito_onefile)

def test_parse_rr_and_eltorito_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrandeltoritoonedir")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_and_eltorito_onedir)

def test_parse_joliet_and_eltorito_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandeltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_nofiles)

def test_parse_joliet_and_eltorito_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandeltoritoonefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_onefile)

def test_parse_joliet_and_eltorito_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietandeltoritoonedir")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_onedir)

def test_parse_isohybrid(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("isohybrid")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "isolinux.bin"), 'wb') as outfp:
        with open('/usr/share/syslinux/isolinux.bin', 'rb') as infp:
            outfp.write(infp.read())
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "isolinux.bin", "-no-emul-boot",
                     "-boot-load-size", "4",
                     "-o", str(outfile), str(indir)])
    subprocess.call(["isohybrid", "-v", str(outfile)])

    do_a_test(tmpdir, outfile, check_isohybrid)

def test_parse_joliet_rr_and_eltorito_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietrrandeltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_rr_and_eltorito_nofiles)

def test_parse_joliet_rr_and_eltorito_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietrrandeltoritoonefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_rr_and_eltorito_onefile)

def test_parse_joliet_rr_and_eltorito_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietrrandeltoritoonedir")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_rr_and_eltorito_onedir)

def test_parse_rr_deep_dir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrdeep")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8')
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_deep_dir)

def test_parse_rr_deep(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrdeep")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8')
    with open(os.path.join(str(indir), 'dir1', 'dir2', 'dir3', 'dir4', 'dir5', 'dir6', 'dir7', 'dir8', 'foo'), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_deep)

def test_parse_rr_deep2(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrdeep")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8').mkdir('dir9')
    with open(os.path.join(str(indir), 'dir1', 'dir2', 'dir3', 'dir4', 'dir5', 'dir6', 'dir7', 'dir8', 'dir9', 'foo'), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_deep2)

def test_parse_xa_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xa")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_nofiles)

def test_parse_xa_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xa")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_onefile)

def test_parse_xa_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xa")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_onedir)

def test_parse_sevendeepdirs(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("sevendeepdirs")
    outfile = str(indir)+".iso"
    numdirs = 7
    x = indir
    for i in range(1, 1+numdirs):
        x = x.mkdir("dir%d" % i)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_sevendeepdirs)

def test_parse_xa_joliet_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xajoliet")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_joliet_nofiles)

def test_parse_xa_joliet_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xajolietonefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_joliet_onefile)

def test_parse_xa_joliet_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xajolietonefile")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_xa_joliet_onedir)

def test_parse_iso_level4_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("isolevel4nofiles")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_isolevel4_nofiles)

def test_parse_iso_level4_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("isolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_isolevel4_onefile)

def test_parse_iso_level4_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("isolevel4onedir")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1')
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_isolevel4_onedir)

def test_parse_iso_level4_eltorito(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("isolevel4eltorito")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_isolevel4_eltorito)

def test_parse_everything(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("everything")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8')
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    with open(os.path.join(str(indir), 'dir1', 'dir2', 'dir3', 'dir4', 'dir5', 'dir6', 'dir7', 'dir8', "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("foo", "sym")
    os.chdir(pwd)
    os.link(os.path.join(str(indir), "foo"), os.path.join(str(indir), 'dir1', "foo"))
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-rational-rock", "-xa", "-boot-info-table",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_everything)

def test_parse_rr_xa_nofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xarrnofiles")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_xa_nofiles)

def test_parse_rr_xa_onefile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xarronefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_xa_onefile)

def test_parse_rr_xa_onedir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("xarronefile")
    outfile = str(indir)+".iso"
    indir.mkdir("dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-xa", "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_xa_onedir)

def test_parse_rr_joliet_symlink(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrsymlinkbroken")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    pwd = os.getcwd()
    os.chdir(str(indir))
    os.symlink("foo", "sym")
    os.chdir(pwd)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_joliet_symlink)

def test_parse_rr_joliet_deep(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrjolietdeep")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8')
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_joliet_deep)

def test_parse_eltorito_multi_boot(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("multiboot")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    with open(os.path.join(str(indir), "boot2"), 'wb') as outfp:
        outfp.write("boot2\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-b", "boot", "-c", "boot.cat", "-no-emul-boot",
                     "-eltorito-alt-boot", "-b", "boot2", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_multi_boot)

def test_parse_eltorito_boot_table(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("boottable")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-b", "boot", "-c", "boot.cat", "-no-emul-boot",
                     "-boot-info-table", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_boot_info_table)

def test_parse_eltorito_boot_table_large(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("boottable")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot"*20)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-b", "boot", "-c", "boot.cat", "-no-emul-boot",
                     "-boot-info-table", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_boot_info_table_large)

def test_parse_hard_link(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("boottable")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    dir1 = indir.mkdir('dir1')
    os.link(os.path.join(str(indir), "foo"), os.path.join(str(indir), str(dir1), "foo"))
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_hard_link)

def test_parse_open_twice(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()
    iso.open(str(outfile))

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

    iso.close()

def test_parse_get_and_write_fp_not_initialized(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.get_and_write_fp('/FOO.;1', open(os.path.join(str(tmpdir), 'bar'), 'w'))

def test_parse_get_and_write_not_initialized(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.get_and_write('/FOO.;1', 'foo')

def test_parse_write_not_initialized(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.write('out.iso')

def test_parse_write_with_progress(tmpdir):
    test_parse_write_with_progress.num_progress_calls = 0
    test_parse_write_with_progress.done = 0
    def _progress(done, total):
        assert(total == 73728)
        test_parse_write_with_progress.num_progress_calls += 1
        test_parse_write_with_progress.done = done

    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-rational-rock", "-J", "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()
    iso.open(str(outfile))
    iso.write(str(tmpdir.join("writetest.iso")), progress_cb=_progress)

    assert(test_parse_write_with_progress.num_progress_calls == 16)
    assert(test_parse_write_with_progress.done == 73728)

    iso.close()

def test_parse_get_entry(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()
    iso.open(str(outfile))

    fooentry = iso.get_entry("/FOO.;1")
    assert(len(fooentry.children) == 0)
    assert(fooentry.isdir == False)
    assert(fooentry.is_root == False)
    assert(fooentry.file_ident == "FOO.;1")
    assert(fooentry.dr_len == 40)
    assert(fooentry.extent_location() == 24)
    assert(fooentry.file_flags == 0)
    assert(fooentry.file_length() == 4)

    iso.close()

def test_parse_get_entry_not_initialized(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        fooentry = iso.get_entry("/FOO.;1")

def test_parse_list_dir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(dir1), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()
    iso.open(str(outfile))

    for children in iso.list_dir("/DIR1"):
        pass

    iso.close()

def test_parse_list_dir_not_initialized(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(dir1), "bar"), 'wb') as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        for children in iso.list_dir("/DIR1"):
            pass

def test_parse_list_dir_not_dir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("twofile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pycdlib and check some things out.
    iso = pycdlib.PyIso()

    iso.open(str(outfile))

    with pytest.raises(pycdlib.PyIsoException):
        for children in iso.list_dir("/FOO.;1"):
            pass

    iso.close()

def test_parse_get_and_write(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("f\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()
    iso.open(str(outfile))

    iso.get_and_write('/foo', os.path.join(str(indir), 'foo'))

    iso.close()

def test_parse_open_fp_twice(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    iso = pycdlib.PyIso()

    iso.open(str(outfile))

    with pytest.raises(pycdlib.PyIsoException):
        with open(str(outfile), 'rb') as infp:
            iso.open_fp(infp)

def test_parse_open_invalid_vd(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek(16*2048)
        fp.write('\xF4')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_same_dirname_different_parent(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("samedirnamedifferentparent")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    dir2 = indir.mkdir("dir2")
    boot1 = dir1.mkdir("boot")
    boot2 = dir2.mkdir("boot")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-rational-rock",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_same_dirname_different_parent)

def test_parse_joliet_iso_level_4(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietisolevel4")
    outfile = str(indir)+".iso"
    dir1 = indir.mkdir("dir1")
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_isolevel4)

def test_parse_eltorito_nofiles_hide(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-hide", "boot.cat",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_nofiles_hide)

def test_parse_eltorito_nofiles_hide_joliet(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-hide", "boot.cat", "-hide-joliet", "boot.cat",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_nofiles_hide)

def test_parse_eltorito_nofiles_hide_joliet_only(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-hide-joliet", "boot.cat",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_nofiles_hide_only)

def test_parse_eltorito_nofiles_hide_iso_only_joliet(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-J", "-hide", "boot.cat",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_and_eltorito_nofiles_hide_iso_only)

def test_parse_hard_link_reshuffle(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("boottable")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), 'wb') as outfp:
        outfp.write("foo\n")
    os.link(os.path.join(str(indir), "foo"), os.path.join(str(indir), "bar"))
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_hard_link_reshuffle)

def test_parse_open_invalid_pvd_ident(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+5)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+6)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_unused1(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+7)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_unused2(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+72)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_unused3(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+88)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_file_structure_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+881)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_unused4(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+882)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_pvd_unused5(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)-1)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_pvd_space_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+84)
        fp.write('\x00\x00\x00\x00')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_pvd_set_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+122)
        fp.write('\x00\x44')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_pvd_seqnum_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+126)
        fp.write('\x00\x44')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_pvd_lb_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+130)
        fp.write('\x00\x01')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_pvd_ptr_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((16*2048)+136)
        fp.write('\x00\x01\x00\x00')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_vdst_ident(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+5)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_vdst_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+6)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_br_ident(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+5)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_br_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritonofiles")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+6)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_ident(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+5)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+6)
        fp.write('\x03')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_unused1(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+72)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_file_structure_version(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+881)
        fp.write('\x03')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_unused2(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+882)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_open_invalid_svd_unused3(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((18*2048)-1)
        fp.write('\x02')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_svd_space_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+84)
        fp.write('\x00\x00\x00\x00')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_svd_set_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+122)
        fp.write('\x00\x44')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_svd_seqnum_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+126)
        fp.write('\x00\x44')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_svd_lb_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+130)
        fp.write('\x00\x01')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_invalid_svd_ptr_size_le_be_mismatch(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("modifyinplaceisolevel4onefile")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    # Now that we've made a valid ISO, we open it up and perturb the first
    # byte.  This should be enough to make an invalid ISO.
    with open(str(outfile), 'r+b') as fp:
        fp.seek((17*2048)+136)
        fp.write('\x00\x01\x00\x00')

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_iso_too_small(tmpdir):
    indir = tmpdir.mkdir("isotoosmall")
    outfile = str(indir)+".iso"
    with open(outfile, 'wb') as outfp:
        outfp.write("\x00"*16*2048)

    iso = pycdlib.PyIso()

    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_rr_deeper_dir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("rrdeep")
    outfile = str(indir)+".iso"
    indir.mkdir('dir1').mkdir('dir2').mkdir('dir3').mkdir('dir4').mkdir('dir5').mkdir('dir6').mkdir('dir7').mkdir('dir8')
    indir.mkdir('a1').mkdir('a2').mkdir('a3').mkdir('a4').mkdir('a5').mkdir('a6').mkdir('a7').mkdir('a8')
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-rational-rock", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_rr_deeper_dir)

def test_parse_eltorito_boot_table_odd(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("boottable")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boo"*27)
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "4", "-no-pad",
                     "-b", "boot", "-c", "boot.cat", "-no-emul-boot",
                     "-boot-info-table", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_boot_info_table_large_odd)

def test_parse_joliet_large_directory(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("jolietlargedirectory")
    outfile = str(indir)+".iso"
    for i in range(1, 50):
        indir.mkdir("dir" + str(i))
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-J", "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_joliet_large_directory)

def test_parse_zero_byte_file(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("zerobytefile")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "foo"), "wb") as outfp:
        pass
    with open(os.path.join(str(indir), "bar"), "wb") as outfp:
        outfp.write("bar\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_zero_byte_file)

def test_parse_dirrecord_too_short(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("tooshort")
    outfile = str(indir)+".iso"
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    with open(outfile, 'a+b') as editfp:
        os.ftruncate(editfp.fileno(), 47104)

    iso = pycdlib.PyIso()
    with pytest.raises(pycdlib.PyIsoException):
        iso.open(str(outfile))

def test_parse_eltorito_hide_boot(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    indir = tmpdir.mkdir("eltoritohideboot")
    outfile = str(indir)+".iso"
    with open(os.path.join(str(indir), "boot"), 'wb') as outfp:
        outfp.write("boot\n")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-c", "boot.cat", "-b", "boot", "-no-emul-boot",
                     "-hide", "boot",
                     "-o", str(outfile), str(indir)])

    do_a_test(tmpdir, outfile, check_eltorito_hide_boot)
