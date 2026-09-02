@echo off
echo ============================================================
echo       AI ENGINE - Complete Installation Script
echo       Python 3.12 Compatible Version
echo ============================================================

echo.
echo [1/4] Installing PyTorch and PyTorch Geometric...
echo.
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
pip install torch-geometric==2.6.1
pip install torch-scatter --no-deps -f https://data.pyg.org/whl/torch-2.5.1+cpu.html
pip install torch-sparse --no-deps -f https://data.pyg.org/whl/torch-2.5.1+cpu.html
pip install torch-cluster --no-deps -f https://data.pyg.org/whl/torch-2.5.1+cpu.html

echo.
echo [2/4] Installing Data Processing Libraries...
echo.
pip install numpy==1.26.4
pip install pandas==2.2.0
pip install scikit-learn==1.5.0
pip install scipy==1.13.0

echo.
echo [3/4] Installing Deep Learning Utilities...
echo.
pip install matplotlib==3.8.4
pip install seaborn==0.13.2
pip install tqdm==4.66.5
pip install tensorboard==2.17.1

echo.
echo [4/4] Installing Web Framework and Utilities...
echo.
pip install fastapi==0.115.6
pip install "uvicorn[standard]==0.34.0"
pip install pydantic==2.10.4
pip install pydantic-settings==2.6.1
pip install neo4j==5.26.0
pip install pymongo==4.10.1
pip install python-dotenv==1.0.1
pip install python-json-logger==3.0.0
pip install joblib==1.4.2
pip install pyyaml==6.0.2
pip install pytest==8.3.4
pip install pytest-asyncio==0.24.0
pip install pytest-cov==6.0.0
pip install httpx==0.28.1

echo.
echo ============================================================
echo       Installation Complete! 🎉
echo ============================================================
echo.
echo Verify installation by running:
echo   python -c "import torch; print('PyTorch:', torch.__version__)"
echo   python -c "import torch_geometric; print('PyG:', torch_geometric.__version__)"
echo.
pause