"""Build local teaching read models, then serve only on loopback."""
from pathlib import Path
import argparse, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('--port must be in 1024..65535')
    try:
        from backend.build import build, RAW
        if not (RAW / 'telemetry.csv').is_file():
            raise FileNotFoundError('Missing supplied fixtures. Run python -m backend.seed to recreate synthetic data.')
        build()
        import uvicorn
        print(f'\nSignal Atlas: http://127.0.0.1:{args.port}\nSynthetic data only. Stop with Ctrl+C.\n')
        uvicorn.run('backend.app:app', host='127.0.0.1', port=args.port, access_log=False)
    except (ImportError, FileNotFoundError, ValueError) as exc:
        print(f'Could not start the lab: {exc}', file=sys.stderr)
        print('Install requirements.txt in your active virtual environment first.', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
