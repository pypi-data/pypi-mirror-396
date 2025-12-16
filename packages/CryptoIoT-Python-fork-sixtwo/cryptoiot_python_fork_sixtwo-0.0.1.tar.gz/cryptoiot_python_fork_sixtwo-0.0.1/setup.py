from setuptools import setup, find_packages

setup(
    name="CryptoIoT-Python-fork-sixtwo",
    version="0.0.1",
    install_requires=[],
    extras_require={
        "full": [
            "pyserial",
            "pycryptodome"
        ],
        "crypto": [
            "pycryptodome"
        ]
    },
    py_modules = ["ciot_client2"],
    entry_points={
        'console_scripts': [
            'ciot-client-62=ciot_client2:main',
        ],
    },
    python_requires='>=3.6',
    description="CIoT Python Cient",
    author="David Wischnjak",
    url="https://github.com/wladimir-computin/CryptoIoT-Python"
)
