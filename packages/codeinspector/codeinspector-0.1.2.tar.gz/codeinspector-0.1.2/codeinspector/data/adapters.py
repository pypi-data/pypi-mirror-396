"""Data adapters for various storage backends"""

import click


class MongoAdapter:
    """MongoDB Atlas adapter"""
    def list_resources(self):
        click.echo("📂 MongoDB collections: (placeholder)")


class SpannerAdapter:
    """Cloud Spanner adapter"""
    def list_resources(self):
        click.echo("📂 Spanner tables: (placeholder)")


class SQLAdapter:
    """Generic SQL adapter"""
    def list_resources(self):
        click.echo("📂 SQL tables: (placeholder)")


class BigQueryAdapter:
    """BigQuery adapter"""
    def list_resources(self):
        click.echo("📂 BigQuery datasets: (placeholder)")


class GCSAdapter:
    """Google Cloud Storage adapter"""
    def list_resources(self):
        click.echo("📂 GCS buckets: (placeholder)")
