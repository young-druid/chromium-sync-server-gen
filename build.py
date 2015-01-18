#!/usr/bin/env python
import argparse
import contextlib
import os
import sys
import tarfile
import tempfile
import urllib2
import shutil


def get_parser():
    parser = argparse.ArgumentParser(prog='Chrome sync server build wrapper',
                                     description='Utility which helps to '
                                                 'generate ready to use chrome '
                                                 'sync server')
    parser.add_argument('-t', '--tag', required=False, default='master',
                        help='Tag name to use (it is usually the same as the '
                             'build number of your Chrome browser)')
    parser.add_argument('-o', '--out', required=False,
                        default=os.getcwd(),
                        help='Output directory where to put chrome sync server')
    parser.add_argument('-p', '--protoc', required=True,
                        help='Path to a protobuf compiler')
    return parser


def unpack_google_files(to_dir, tag, src_folder):
    base_url = 'https://chromium.googlesource.com/chromium/src/+archive/' + tag
    response = urllib2.urlopen(base_url + src_folder)
    with tempfile.TemporaryFile() as tmp_f:
        shutil.copyfileobj(response, tmp_f)
        tmp_f.flush()
        tmp_f.seek(0)
        tar = tarfile.open(fileobj=tmp_f, mode='r:gz')
        tar.extractall(path=to_dir)
        tar.close()


@contextlib.contextmanager
def redirect_argv(work_dir, tmp_dir, filename, protoc_path):
    _argv = sys.argv[:]
    sys.argv = [os.path.join(tmp_dir, 'protoc_wrapper', 'protoc_wrapper.py'),
                '--proto-in-dir', os.path.join(tmp_dir, 'protocol'),
                '--proto-in-file', filename, '--use-system-protobuf', '1', '--',
                protoc_path, '--python_out=' + work_dir]
    yield
    sys.argv = _argv


def compile_protocols(work_dir, tmp_dir, protoc_path):
    from protoc_wrapper import protoc_wrapper
    for filename in os.listdir(os.path.join(tmp_dir, 'protocol')):
        if filename.endswith('.proto'):
            with redirect_argv(work_dir, tmp_dir, filename, protoc_path):
                if protoc_wrapper.main(sys.argv) == 0:
                    continue
                else:
                    return 1
    return 0


def unpack_utility_files(to_dir, tag):
    pw_path = os.path.join(to_dir, 'protoc_wrapper')
    unpack_google_files(pw_path, tag, '/tools/protoc_wrapper.tar.gz')
    open(os.path.join(pw_path, '__init__.py'), 'w+').close()
    sys.path.append(to_dir)
    unpack_google_files(os.path.join(to_dir, 'protocol'), tag,
                        '/sync/protocol.tar.gz')


def unpack_server_files(work_dir, tag):
    unpack_google_files(work_dir, tag, '/sync/tools/testserver.tar.gz')
    unpack_google_files(work_dir, tag, '/net/tools/testserver.tar.gz')


def main(args):
    args = get_parser().parse_args(args)
    tmp_dir = tempfile.mkdtemp()
    try:
        unpack_utility_files(tmp_dir, args.tag)
        unpack_server_files(args.out, args.tag)
        return compile_protocols(args.out, tmp_dir, args.protoc)
    finally:
        shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))