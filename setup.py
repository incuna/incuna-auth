from setuptools import find_packages, setup


install_requires = ('django-admin-sso', 'django-crispy-forms')

setup(
    name='incuna-auth',
    version='2.3.4',
    url='http://github.com/incuna/incuna-auth',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    description='Provides authentication parts.',
    long_description=open('README.rst').read(),
    author='Incuna Ltd',
    author_email='admin@incuna.com',
)
