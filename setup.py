from setuptools import find_packages, setup


install_requires = ('django-admin-sso',)

setup(
    name='incuna-auth',
    version='0.7.2',
    url='http://github.com/incuna/incuna-auth',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    description='Provides authentication parts.',
    long_description=open('README.rst').read(),
    author='Incuna Ltd',
    author_email='admin@incuna.com',
)
