from setuptools import setup


install_requires = ('django-admin-sso',)

setup(
    name='incuna-auth-urls',
    version='0.1',
    url='http://github.com/incuna/incuna-auth-urls',
    py_modules=('auth_urls',),
    include_package_data=True,
    install_requires=install_requires,
    description='Provides authentication parts.',
    long_description=open('README.rst').read(),
    author='Incuna Ltd',
    author_email='admin@incuna.com',
)

