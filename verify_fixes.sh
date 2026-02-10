#!/bin/bash

echo "=========================================="
echo "Verifying Django Admin Fixes"
echo "=========================================="
echo ""

# Check if web container is running
echo "1. Checking web container status..."
docker compose ps web | grep "Up" && echo "✅ Web container is running" || echo "❌ Web container is not running"
echo ""

# Check if static files exist
echo "2. Checking static files..."
[ -f "static/js/admin-actions.js" ] && echo "✅ admin-actions.js exists" || echo "❌ admin-actions.js missing"
[ -f "staticfiles/js/admin-actions.js" ] && echo "✅ admin-actions.js collected to staticfiles" || echo "❌ admin-actions.js not in staticfiles"
echo ""

# Check if code changes exist
echo "3. Checking code changes..."
grep -q "{0}%" apps/devices/admin.py && echo "✅ charge_bar format fix applied" || echo "❌ charge_bar not fixed"
grep -q "CustomUserAdmin" apps/devices/admin.py && echo "✅ CustomUserAdmin class exists" || echo "❌ CustomUserAdmin missing"
echo ""

# Check for recent errors in logs
echo "4. Checking for 500 errors in recent logs..."
ERROR_COUNT=$(docker compose logs web --tail=200 | grep -c "500 Internal Server Error")
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ No 500 errors found in recent logs"
else
    echo "⚠️  Found $ERROR_COUNT 500 errors in logs"
fi
echo ""

# Test if battery admin endpoint is accessible (without auth)
echo "5. Testing Batteries admin endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/admin/devices/battery/")
if [ "$HTTP_CODE" -eq "302" ]; then
    echo "✅ Batteries endpoint accessible (302 redirect to login - expected)"
elif [ "$HTTP_CODE" -eq "500" ]; then
    echo "❌ Batteries endpoint returning 500 error"
else
    echo "⚠️  Batteries endpoint returned HTTP $HTTP_CODE"
fi
echo ""

echo "=========================================="
echo "Manual Testing Required:"
echo "=========================================="
echo "1. Open http://localhost:8000/admin/auth/user/"
echo "2. Login with admin/admin123"
echo "3. Verify action dropdown shows 'Delete selected users' (no 'none' option)"
echo "4. Click 'Batteries' in sidebar - should load without error"
echo "5. Verify text in action dropdown is white and visible"
echo ""
echo "All automated checks complete!"
