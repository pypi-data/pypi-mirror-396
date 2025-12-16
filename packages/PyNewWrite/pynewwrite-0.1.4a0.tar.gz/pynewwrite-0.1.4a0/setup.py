from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='PyNewWrite',
  version='0.1.4A',
  author='Sigard_Vinter',
  author_email='developer.vinter@gmail.com',
  description='Новый спопоб вывода кода в Python',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/EvgenEvkal',
  packages=find_packages(),
  package_data={"PyNewWrite": ["data/**/*"]},
  include_package_data=True,
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='example python',
  project_urls={
    'Documentation': 'https://github.com/EvgenEvkal'
  },
  python_requires='>=3.7',
)