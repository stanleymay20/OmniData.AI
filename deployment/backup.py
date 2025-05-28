#!/usr/bin/env python3
import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

def create_backup_dir():
    """Create backup directory if it doesn't exist."""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def backup_database(config):
    """Backup PostgreSQL database."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = create_backup_dir()
    backup_file = backup_dir / f'db_backup_{timestamp}.sql'
    
    try:
        subprocess.run([
            'pg_dump',
            '-h', config['database']['host'],
            '-p', str(config['database']['port']),
            '-U', config['database']['user'],
            '-d', config['database']['name'],
            '-f', str(backup_file)
        ], check=True, env={'PGPASSWORD': config['database']['password']})
        print(f"Database backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Database backup failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def backup_redis():
    """Backup Redis data."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = create_backup_dir()
    backup_file = backup_dir / f'redis_backup_{timestamp}.rdb'
    
    try:
        subprocess.run([
            'docker', 'cp',
            'redis:/data/dump.rdb',
            str(backup_file)
        ], check=True)
        print(f"Redis backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Redis backup failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def backup_mlflow():
    """Backup MLflow artifacts."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = create_backup_dir()
    backup_file = backup_dir / f'mlflow_backup_{timestamp}.tar.gz'
    
    try:
        subprocess.run([
            'docker', 'exec',
            'mlflow',
            'tar', '-czf', '/tmp/mlflow_backup.tar.gz',
            '/mlflow'
        ], check=True)
        
        subprocess.run([
            'docker', 'cp',
            'mlflow:/tmp/mlflow_backup.tar.gz',
            str(backup_file)
        ], check=True)
        print(f"MLflow backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"MLflow backup failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def restore_database(config, backup_file):
    """Restore PostgreSQL database from backup."""
    try:
        subprocess.run([
            'psql',
            '-h', config['database']['host'],
            '-p', str(config['database']['port']),
            '-U', config['database']['user'],
            '-d', config['database']['name'],
            '-f', str(backup_file)
        ], check=True, env={'PGPASSWORD': config['database']['password']})
        print(f"Database restored from: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Database restore failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def restore_redis(backup_file):
    """Restore Redis data from backup."""
    try:
        subprocess.run([
            'docker', 'cp',
            str(backup_file),
            'redis:/data/dump.rdb'
        ], check=True)
        
        subprocess.run([
            'docker', 'restart',
            'redis'
        ], check=True)
        print(f"Redis restored from: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Redis restore failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def restore_mlflow(backup_file):
    """Restore MLflow artifacts from backup."""
    try:
        subprocess.run([
            'docker', 'cp',
            str(backup_file),
            'mlflow:/tmp/mlflow_backup.tar.gz'
        ], check=True)
        
        subprocess.run([
            'docker', 'exec',
            'mlflow',
            'tar', '-xzf', '/tmp/mlflow_backup.tar.gz',
            '-C', '/'
        ], check=True)
        
        subprocess.run([
            'docker', 'restart',
            'mlflow'
        ], check=True)
        print(f"MLflow restored from: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"MLflow restore failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Backup and restore OmniData.AI services')
    parser.add_argument('--action', choices=['backup', 'restore'],
                      required=True, help='Action to perform')
    parser.add_argument('--service', choices=['all', 'db', 'redis', 'mlflow'],
                      default='all', help='Service to backup/restore')
    parser.add_argument('--backup-file', help='Backup file to restore from')
    args = parser.parse_args()

    # Load configuration
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path) as f:
        import yaml
        config = yaml.safe_load(f)['environments']['production']

    if args.action == 'backup':
        if args.service in ['all', 'db']:
            backup_database(config)
        if args.service in ['all', 'redis']:
            backup_redis()
        if args.service in ['all', 'mlflow']:
            backup_mlflow()
    else:  # restore
        if not args.backup_file:
            print("Backup file is required for restore", file=sys.stderr)
            sys.exit(1)
        
        backup_file = Path(args.backup_file)
        if not backup_file.exists():
            print(f"Backup file not found: {backup_file}", file=sys.stderr)
            sys.exit(1)
        
        if args.service in ['all', 'db']:
            restore_database(config, backup_file)
        if args.service in ['all', 'redis']:
            restore_redis(backup_file)
        if args.service in ['all', 'mlflow']:
            restore_mlflow(backup_file)

if __name__ == '__main__':
    main() 