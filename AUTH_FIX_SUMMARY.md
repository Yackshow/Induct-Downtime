# Authentication Fix Summary

## What Was Done

The `src/auth.py` file has been updated with the exact authentication pattern from your working code:

### Key Changes Made:

1. **Headers Set Before Cookies** (Line 90-94)
   - Headers are now set BEFORE loading cookies, which is critical
   - Uses exact headers: `Accept: application/json` and `User-Agent: AmzBot/1.0`

2. **Session Management** (Line 82-83)
   - Session is closed and recreated each time for fresh authentication
   - Prevents stale session issues

3. **Cookie Loading** (Line 31-66)
   - Exact cookie parsing logic matching your working pattern
   - Handles `#HttpOnly_` domain prefix correctly
   - Sets all cookie attributes properly

4. **Session Establishment** (Line 109-118)
   - Makes initial request to `https://logistics.amazon.com/station/dashboard/ageing`
   - Checks for login redirects to detect auth failures

5. **SSL and Redirect Handling** (Line 97-98)
   - SSL verification disabled for internal Mercury
   - Redirects disabled to catch auth failures

## What You Need To Do

### 1. Install Python Packages
Since pip is not available on your system, you have a few options:

```bash
# Option A: Install pip first
sudo apt-get update
sudo apt-get install python3-pip

# Then install packages
pip3 install -r requirements.txt
```

```bash
# Option B: Install via system packages
sudo apt-get install python3-requests python3-bs4 python3-yaml
```

```bash
# Option C: Use a Python environment that has pip
# (e.g., PyCharm's virtual environment, conda, etc.)
```

### 2. Run From Correct Location
The cookie file is at `/home/mackhun/.midway/cookie`, so either:

```bash
# Option A: Run as your user from your directory
cd /local/home/mackhun/PycharmProjects/Induct-Downtime
python3 src/auth.py

# Option B: Copy cookie to current environment
mkdir -p ~/.midway
cp /home/mackhun/.midway/cookie ~/.midway/cookie
python3 src/auth.py
```

### 3. Test the Authentication
Once packages are installed and cookie is accessible:

```bash
# Test authentication module
python3 src/auth.py

# Test full Mercury scraper
python3 debug_mercury.py
```

## The Updated Code Structure

The authentication now follows this exact flow:
1. Create session with retry adapter
2. Set headers (BEFORE cookies!)
3. Set SSL and redirect options
4. Load cookies from file
5. Add Kerberos/SSPI auth if available
6. Make establishment request
7. Check for login redirects
8. Return authenticated session

This matches your working code pattern exactly. The only missing pieces are the Python packages and proper environment setup.