'''
    pip setup file
    --------------
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import os
import codecs
import glob
import setuptools

_readme_filename = 'README.rst'
package_dir = {'': 'packages'}

def get_long_description():
    current_directory = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(current_directory, _readme_filename), encoding='utf-8') as f:
        return f.read()
        
def get_no_init_packages(package_root):
    is_found = False
    walk = os.walk(package_root)
    while not is_found:
        (root, directories, files) = next(walk)
        for dir_relative_to_root in directories:
            dir_relative_to_setup = os.path.join(root, dir_relative_to_root)
            relative_path = os.path.relpath(dir_relative_to_setup, package_dir[''])
            package = relative_path.replace('/', '.')
            if package not in packages:
                packages.append(package)
                is_found = True
                
def get_package_data(path_to_package):
    result = []
    for (root, directories, files) in os.walk(path_to_package):
        #if '__init__.py' in files: continue
        relpath = os.path.relpath(root, path_to_package)
        for f in files:
            if not f.endswith('.pyc'):
                result.append(os.path.join(relpath, f))
    return result
    
def get_packages_and_data(package_root):
    package_data = {'': ['*.txt', '*.rst']}
    packages = setuptools.find_packages(package_root)
    packages.reverse()
    for p in packages:
        path_to_package = os.path.join(package_root, p.replace('.', '/'))
        package_data[p] = get_package_data(path_to_package)
    return (packages, package_data)
    
def get_data_files(patterns):
    result = []
    for pattern in patterns:
        result.extend(glob.glob(pattern))
    return result
    
(packages, package_data) = get_packages_and_data(package_dir[''])

setuptools.setup(
    name='ASMO',
    version='0.4',
    description='Attentive Self-Modifying Cognitive Architecture',
    long_description=get_long_description(),
    url='https://github.com/airobots/asmo_python',
    author='Rony Novianto',
    author_email='rony@ronynovianto.com',
    license='BSD',
    classifiers=\
    [
        'Environment :: MacOS X',
        'Environment :: Web Environment',
        'Environment :: Win32 (MS Windows)',
        'Environment :: Other Environment',
        'Framework :: Robot Framework',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='asmo cognitive architecture',
    install_requires=['tornado', 'requests_futures'],
    include_package_data=True,
    package_dir=package_dir,
    packages=setuptools.find_packages(package_dir['']),
    data_files=\
    [
        ('asmo', get_data_files(['*.rst', 'LICENSE.txt'])),
        ('asmo/examples', get_data_files(['examples/*.py'])),
        ('asmo/virtualenv', get_data_files(['virtualenv/*.py'])),
    ],
)
