from setuptools import setup
import re

requirements = [
  "requests",
  "python-olm"
]
# with open('requirements.txt') as f:
#   requirements = f.read().splitlines()

# version = ''
# with open('matrix/__init__.py') as f:
#     version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

# if not version:
#     raise RuntimeError('version is not set')

# if version.endswith(('a', 'b', 'rc')):
#     # append version identifier based on commit count
#     try:
#         import subprocess
#         p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
#                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = p.communicate()
#         if out:
#             version += out.decode('utf-8').strip()
#         p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
#                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = p.communicate()
#         if out:
#             version += '+g' + out.decode('utf-8').strip()
#     except Exception:
#         pass

readme = ''
with open('README.md') as f:
    readme = f.read()

# extras_require = {
#     'voice': ['PyNaCl>=1.3.0,<1.5'],
#     'docs': [
#         'sphinx==4.0.2',
#         'sphinxcontrib_trio==1.1.2',
#         'sphinxcontrib-websupport',
#     ],
#     'speed': [
#         'orjson>=3.5.4',
#     ]
# }

version = '0.0.1.2'

packages = [
    'matrix',
]

setup(name='matrix-chat',
      author='Peet',
      url='https://github.com/wwhtrbbtt/matrix.py',
      author_email="matrix@peet.ws",

      project_urls={
        "Documentation": "https://matrixpy.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/wwhtrbbtt/matrix.py/issues",
      },
      version=version,
      packages=packages,
      license='MIT',
      description='A Python wrapper for the Matrix API',
      long_description=readme,
      long_description_content_type='text/markdown',
      include_package_data=True,
      install_requires=requirements,
    #   extras_require=extras_require,
      python_requires='>=3.8.0',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
      ]
)