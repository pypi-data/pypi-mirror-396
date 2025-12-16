from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ultrarag",
    version="1.0.0",
    author="Abhishek Kumar",
    author_email="ipsabhi420@gmail.com",
    description="Complete RAG with built-in Ollama + FastAPI + Swagger - Zero Config!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kumar123ips/ultrarag",
    py_modules=["ultrarag"],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",  # For Ollama
    ],
    extras_require={
        'server': [
            'fastapi>=0.104.1',
            'uvicorn[standard]>=0.24.0',
            'python-multipart>=0.0.6',
        ],
    },
    entry_points={
        'console_scripts': [
            'ultrarag=ultrarag:cli',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="rag llm chatbot ollama fastapi swagger zero-config",
)
