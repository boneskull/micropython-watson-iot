import glob
import io
import os
import re
import tarfile
import zlib

from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

FILTERS = [
    # include, exclude, repeat
    (r'.+\.egg-info/(PKG-INFO|requires\.txt)', r'setup.py$'),
    (r'.+\.py$', r'[^/]+$'),
    (None, r'.+\.egg-info/.+'),
]


class UpipSdist(sdist):
    """
    This Command will optimize the distribution tarball for installation
    via upip.

    It removes files unused by upip (including this one) and re-compresses
    the tarball for use on low-memory devices
    """

    user_options = []
    outbuf = io.BytesIO()

    def run(self):
        super(UpipSdist, self).run()
        latest = UpipSdist.find_latest('dist')
        orig_size = os.stat(latest).st_size
        self.filter_tar(latest)
        self.outbuf.seek(0)
        self.gzip_4k(latest)
        new_size = os.stat(latest).st_size
        print(f"""Recompressed {latest}.

    Original size: {orig_size} bytes
Recompressed size: {new_size} bytes
       Difference: {orig_size - new_size} bytes
""")

    @staticmethod
    def find_latest(dir):
        res = []
        for fname in glob.glob(f'{dir}/*.gz'):
            st = os.stat(fname)
            res.append((st.st_mtime, fname))
        res.sort()
        latest = res[-1][1]
        return latest

    def gzip_4k(self, fname):
        inf = self.outbuf
        comp = zlib.compressobj(level=9, wbits=16 + 12)
        with open(f'{fname}.out', 'wb') as outf:
            data = inf.read(1024)
            while data:
                outf.write(comp.compress(data))
                data = inf.read(1024)
            outf.write(comp.flush())
        os.rename(fname, f'{fname}.orig')
        os.rename(f'{fname}.out', fname)

    def filter_tar(self, name):
        fin = tarfile.open(name, 'r:gz')
        fout = tarfile.open(fileobj=self.outbuf, mode='w')
        for info in [x for x in fin if '/' in x.name]:
            fname = info.name.split('/', 1)[1]
            include = None

            for inc_re, exc_re in FILTERS:
                if include is None and inc_re and re.match(inc_re, fname):
                    include = True

                if include is None and exc_re and re.match(exc_re, fname):
                    include = False

            if include or include is None:
                print(f'Including: {fname}')
                farch = fin.extractfile(info)
                fout.addfile(info, farch)
            else:
                print(f'Excluding: {fname}')

        fout.close()
        fin.close()


setup(
    name='micropython-ibmiotf',
    version='0.0.1',
    packages=find_packages(),
    description='Unofficial IBM Watson IoT Platform SDK for Devices Running Micropython',
    url='https://github.com/boneskull/micropython-ibmiotf',
    author='Christopher Hiller',
    author_email='boneskull@boneskull.com',
    maintainer='Christopher Hiller',
    maintainer_email='boneskull@boneskull.com',
    license='Apache-2.0',
    install_requires=(
        'micropython-umqtt.simple>=1.3.4', 'micropython-umqtt.robust>=1.0',
        'micropython-logging>=0.1.3'),
    cmdclass=dict(sdist=UpipSdist)
)
