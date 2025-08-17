#!/bin/bash

# FinWise Local Development Setup Script
# This script sets up and runs the FinWise application locally

echo -e "${BLUE}FinWise Local Development Setup${NC}"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.8+ first"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        echo "Please install Node.js 16+ first"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        echo "Please install npm first"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "finwise_backend/manage.py" ]; then
        print_error "Please run this script from the FinWise project root directory"
        exit 1
    fi
    
    print_success "Prerequisites check completed"
}

# Function to setup backend
setup_backend() {
    echo ""
    print_info "Setting up backend..."
    
    cd finwise_backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << 'EOF'
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Gemini AI Settings
GEMINI_API_KEY=your-gemini-api-key-here

# Database Settings
DATABASE_URL=sqlite:///db.sqlite3
EOF
        
        print_warning "Please update the .env file with your Gemini API key"
        echo "Get your key from: https://makersuite.google.com/app/apikey"
    fi
    
    # Run migrations
    echo "Running database migrations..."
    python manage.py migrate
    
    cd ..
    print_success "Backend setup completed"
}

# Function to setup frontend
setup_frontend() {
    echo ""
    print_info "Setting up frontend..."
    
    cd project_frontend/projectv2_v
    
    # Install dependencies
    echo "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        echo "VITE_API_URL=http://127.0.0.1:8000" > .env
    fi
    
    cd ../..
    print_success "Frontend setup completed"
}

# Function to start backend
start_backend() {
    echo ""
    print_info "Starting Django backend..."
    
    cd finwise_backend
    source venv/bin/activate
    
    # Start backend in background
    nohup python manage.py runserver 127.0.0.1:8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Save PID
    echo $BACKEND_PID > ../backend.pid
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8000/api/health/ > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    cd ..
    
    if [ -f "backend.pid" ]; then
        print_success "Backend started successfully"
        echo "Backend PID: $BACKEND_PID"
        echo "Backend logs: tail -f backend.log"
    else
        print_error "Backend failed to start"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    echo ""
    print_info "Starting React frontend..."
    
    cd project_frontend/projectv2_v
    
    # Start frontend in background
    nohup npm run dev > ../../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Save PID
    echo $FRONTEND_PID > ../../frontend.pid
    
    # Wait for frontend to start
    echo "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    cd ../..
    
    if [ -f "frontend.pid" ]; then
        print_success "Frontend started successfully"
        echo "Frontend PID: $FRONTEND_PID"
        echo "Frontend logs: tail -f frontend.log"
    else
        print_error "Frontend failed to start"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo ""
    print_info "FinWise is now running locally!"
    echo ""
    echo "Access your application:"
    echo "Backend: http://127.0.0.1:8000"
    echo "Frontend: http://localhost:3000"
    echo "Admin Panel: http://127.0.0.1:8000/admin"
    echo ""
    echo "Logs:"
    echo "Backend: tail -f backend.log"
    echo "Frontend: tail -f frontend.log"
    echo ""
    echo "To stop servers: ./run_local.sh stop"
    echo ""
    print_success "Happy coding!"
}

# Function to cleanup
cleanup() {
    echo ""
    print_info "Cleaning up..."
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "Stopped backend process"
        fi
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "Stopped frontend process"
        fi
        rm -f frontend.pid
    fi
    
    print_success "Servers stopped"
}

# Function to show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start   - Start FinWise locally (default)"
    echo "  stop    - Stop all running servers"
    echo "  status  - Show current status"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0        # Start FinWise"
    echo "  $0 stop   # Stop servers"
    echo "  $0 status # Show status"
}

# Main execution
case "${1:-start}" in
    start)
        print_info "Starting FinWise locally..."
        check_prerequisites
        setup_backend
        setup_frontend
        start_backend
        start_frontend
        show_status
        ;;
    stop)
        cleanup
        ;;
    status)
        if [ -f "backend.pid" ] && [ -f "frontend.pid" ]; then
            echo "FinWise is running:"
            echo "Backend PID: $(cat backend.pid)"
            echo "Frontend PID: $(cat frontend.pid)"
        else
            echo "FinWise is not running"
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 