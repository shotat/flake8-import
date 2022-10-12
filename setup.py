from setuptools import setup


def main():
    setup(
        name='flake8-import',
        version='0.0.1',
        zip_safe=False,
        py_modules=['flake8_import'],
        install_requires=[
            'flake8',
            'astpretty',
        ],
        entry_points={
            'flake8.extension': [
                'X = flake8_import:ImportChecker',
            ],
        },
    )


if __name__ == '__main__':
    main()
