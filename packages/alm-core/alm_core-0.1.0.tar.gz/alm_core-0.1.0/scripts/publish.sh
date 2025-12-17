#!/bin/bash

# ALM Core - Build and Publish Script
# This script helps you build and publish the package to PyPI

set -e  # Exit on error

echo "========================================="
echo "ALM Core - Build and Publish Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    print_error "setup.py not found. Please run this script from the ALM root directory."
    exit 1
fi

print_info "Current directory: $(pwd)"

# Step 1: Clean previous builds
print_info "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info
print_info "Cleaned!"

# Step 2: Install build dependencies
print_info "Installing build dependencies..."
pip install -q --upgrade build twine wheel
print_info "Dependencies installed!"

# Step 3: Run tests (optional)
read -p "Run tests before building? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running tests..."
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
    else
        print_warning "pytest not found. Installing..."
        pip install pytest pytest-cov
        pytest tests/ -v
    fi
    print_info "Tests passed!"
fi

# Step 4: Build the package
print_info "Building the package..."
python -m build
print_info "Package built successfully!"

# List built files
print_info "Built files:"
ls -lh dist/

# Step 5: Check the package
print_info "Checking package with twine..."
twine check dist/*
print_info "Package check passed!"

# Step 6: Choose destination
echo ""
echo "Where do you want to upload the package?"
echo "1) TestPyPI (recommended for testing)"
echo "2) PyPI (production)"
echo "3) Skip upload"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        print_info "Uploading to TestPyPI..."
        print_warning "Make sure you have a TestPyPI account and API token!"
        print_info "Get your token at: https://test.pypi.org/manage/account/token/"
        
        twine upload --repository testpypi dist/*
        
        print_info "Upload complete!"
        echo ""
        print_info "Test installation with:"
        echo "  pip install --index-url https://test.pypi.org/simple/ alm-core"
        ;;
    2)
        print_info "Uploading to PyPI (PRODUCTION)..."
        print_warning "Make sure you have a PyPI account and API token!"
        print_info "Get your token at: https://pypi.org/manage/account/token/"
        
        read -p "Are you sure you want to upload to production PyPI? (yes/no) " confirm
        if [ "$confirm" == "yes" ]; then
            twine upload dist/*
            
            print_info "Upload complete!"
            echo ""
            print_info "Installation command:"
            echo "  pip install alm-core"
        else
            print_warning "Upload cancelled."
        fi
        ;;
    3)
        print_info "Skipping upload."
        print_info "You can manually upload later with:"
        echo "  twine upload --repository testpypi dist/*  # For TestPyPI"
        echo "  twine upload dist/*                        # For PyPI"
        ;;
    *)
        print_error "Invalid choice."
        exit 1
        ;;
esac

echo ""
print_info "Done!"
echo ""
echo "========================================="
echo "Next steps:"
echo "1. Test the package installation"
echo "2. Update version in setup.py for next release"
echo "3. Tag the release in git:"
echo "   git tag v0.1.0"
echo "   git push origin v0.1.0"
echo "========================================="
