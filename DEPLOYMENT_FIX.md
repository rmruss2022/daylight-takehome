# Deployment Fix Steps

## Issue
Battery and EV flow showing 0 because:
1. Test data has devices in idle states (batteries at 50%, EV at 90%)
2. GraphQL schema `current_flow_w` field not returning data

## Immediate Fix (SSH into Railway)

```bash
# 1. Navigate to app directory
cd /app

# 2. Update test data (set batteries to charging/discharging states)
python create_test_data.py

# 3. Verify Celery is running the simulation
celery -A config inspect active

# 4. Check if simulation is storing data in Redis
python manage.py shell
>>> from apps.simulation.redis_client import RedisClient
>>> rc = RedisClient()
>>> rc.get_device_storage(1)  # Check battery 1
>>> rc.get_device_storage(2)  # Check battery 2  
>>> rc.get_device_storage(4)  # Check EV
>>> exit()

# 5. If no Redis data, manually trigger simulation
python manage.py run_simulation

# 6. Wait 60 seconds, then check the dashboard
```

## Root Cause Summary

**Backend Code:** ✅ Fixed (commits 9c457b0, 150159a)
- Added `current_flow_w` field to BatteryType and ElectricVehicleType
- Updated resolver to fetch from Redis
- Updated test data to use active charge states

**Deployment:** ⚠️  Need to verify
- Railway should auto-deploy on push
- May need to manually restart or run migrations

**Test Data:** ❌ Not Updated Yet
- Batteries still at 50% (idle range 50-70%)
- Need to run `python create_test_data.py` on Railway

## Expected Result

After fix:
- Home Battery: ~2500 W (charging at 30% capacity)
- Garage Battery: ~-2000 W (discharging at 80% capacity)
- Tesla: ~7000-9000 W (charging at 60%)
- Nissan Leaf: ~5000-6000 W (charging at 65%)
