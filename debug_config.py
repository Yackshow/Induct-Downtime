import sys
sys.path.insert(0, '.')
try:
    from main import InductDowntimeMonitor
    monitor = InductDowntimeMonitor('config.yaml')
    print('Success!')
except Exception as e:
    print(f'Real error: {type(e).__name__}: {e}')
