"""
PostgreSQL Metadata Store Implementation

Stores metadata in PostgreSQL tables within a dedicated schema.
"""

import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import psycopg2  # type: ignore[import-untyped]
from alembic.runtime.migration import MigrationContext
from psycopg2.extras import RealDictCursor  # type: ignore[import-untyped]
from sqlalchemy import create_engine

from pycharter.metadata_store.client import MetadataStoreClient

if TYPE_CHECKING:
    from psycopg2.extensions import (
        connection as Psycopg2Connection,  # type: ignore[import-untyped]
    )
else:
    Psycopg2Connection = Any

try:
    from pycharter.config import get_database_url
except ImportError:
    def get_database_url() -> Optional[str]:  # type: ignore[misc]
        return None


class PostgresMetadataStore(MetadataStoreClient):
    """
    PostgreSQL metadata store implementation.

    Stores metadata in PostgreSQL tables within the specified schema (default: "pycharter"):
    - schemas: JSON Schema definitions
    - governance_rules: Governance rules
    - ownership: Ownership information
    - metadata: Additional metadata
    - coercion_rules: Coercion rules for data transformation
    - validation_rules: Validation rules for data validation

    Connection string format: postgresql://[user[:password]@][host][:port][/database]

    The schema namespace is automatically created if it doesn't exist when connecting.
    However, tables must be initialized separately using 'pycharter db init' (similar to
    'airflow db init'). All tables are created in the specified schema (not in the public schema).

    Example:
        >>> # First, initialize the database schema
        >>> # Run: pycharter db init postgresql://user:pass@localhost/pycharter
        >>>
        >>> # Then connect
        >>> store = PostgresMetadataStore("postgresql://user:pass@localhost/pycharter")
        >>> store.connect()  # Only connects and validates schema
        >>> schema_id = store.store_schema("user", {"type": "object"}, version="1.0")
        >>> store.store_coercion_rules(schema_id, {"age": "coerce_to_integer"}, version="1.0")
        >>> store.store_validation_rules(schema_id, {"age": {"is_positive": {}}}, version="1.0")

    To use a different schema name:
        >>> store = PostgresMetadataStore(
        ...     "postgresql://user:pass@localhost/pycharter",
        ...     schema_name="my_custom_schema"
        ... )
    """

    def __init__(
        self, connection_string: Optional[str] = None, schema_name: str = "pycharter"
    ):
        """
        Initialize PostgreSQL metadata store.

        Args:
            connection_string: Optional PostgreSQL connection string.
                              If not provided, will use configuration from:
                              - PYCHARTER__DATABASE__SQL_ALCHEMY_CONN env var
                              - PYCHARTER_DATABASE_URL env var
                              - pycharter.cfg config file
                              - alembic.ini config file
            schema_name: PostgreSQL schema name to use (default: "pycharter")
        """
        # Try to get connection string from config if not provided
        if not connection_string:
            connection_string = get_database_url()

        if not connection_string:
            raise ValueError(
                "connection_string is required. Provide it directly, or configure it via:\n"
                "  - Environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL\n"
                "  - Config file: pycharter.cfg [database] sql_alchemy_conn\n"
                "  - Config file: alembic.ini sqlalchemy.url"
            )

        super().__init__(connection_string)
        self.schema_name = schema_name
        self._connection: Optional["Psycopg2Connection"] = None

    def connect(self, validate_schema_on_connect: bool = True) -> None:
        """
        Connect to PostgreSQL and validate schema.

        Args:
            validate_schema_on_connect: If True, validate that tables exist after connection

        Raises:
            ValueError: If connection_string is missing
            RuntimeError: If schema validation fails (tables don't exist)

        Note:
            This method only connects and validates. To initialize the database schema,
            run 'pycharter db init' first (similar to 'airflow db init').
        """
        if not self.connection_string:
            raise ValueError("connection_string is required for PostgreSQL")

        self._connection = psycopg2.connect(self.connection_string)
        self._ensure_schema_exists()
        self._set_search_path()

        if validate_schema_on_connect and not self._is_schema_initialized():
            raise RuntimeError(
                "Database schema is not initialized. "
                "Please run 'pycharter db init' to initialize the schema first.\n"
                f"Example: pycharter db init {self.connection_string}"
            )

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    # ============================================================================
    # Connection Management Helpers
    # ============================================================================

    def _ensure_schema_exists(self) -> None:
        """Create the PostgreSQL schema namespace if it doesn't exist."""
        if self._connection is None:
            return

        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema_name}"')
            conn.commit()

    def _set_search_path(self) -> None:
        """Set search_path to use the schema."""
        if self._connection is None:
            return

        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(f'SET search_path TO "{self.schema_name}", public')
            conn.commit()

    def _is_schema_initialized(self) -> bool:
        """Check if the database schema is initialized."""
        if self._connection is None:
            return False

        try:
            with self._connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = 'schemas'
                    )
                """,
                    (self.schema_name,),
                )
                return cur.fetchone()[0]
        except Exception:
            return False

    def _require_connection(self) -> None:
        """Raise error if not connected."""
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")

    def _get_connection(self) -> "Psycopg2Connection":
        """Get connection, raising error if not connected."""
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._connection

    def _parse_jsonb(self, value: Any) -> Dict[str, Any]:
        """Parse JSONB value (psycopg2 may return dict or str)."""
        if isinstance(value, str):
            return json.loads(value)
        return value if value is not None else {}

    def _table_name(self, table: str) -> str:
        """Get fully qualified table name."""
        return f'"{self.schema_name}".{table}'

    # ============================================================================
    # Schema Info
    # ============================================================================

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about the current database schema.

        Returns:
            Dictionary with schema information:
            {
                "revision": str or None,
                "initialized": bool,
                "message": str
            }
        """
        self._require_connection()

        initialized = self._is_schema_initialized()
        revision = None

        if initialized:
            try:
                if self.connection_string is None:
                    raise ValueError("connection_string is required")
                engine = create_engine(self.connection_string)
                with engine.connect() as conn:
                    context = MigrationContext.configure(conn)
                    revision = context.get_current_revision()
            except Exception:
                pass

        message = f"Schema initialized: {initialized}"
        if revision:
            message += f" (revision: {revision})"

        return {
            "revision": revision,
            "initialized": initialized,
            "message": message,
        }

    # ============================================================================
    # Schema Operations
    # ============================================================================

    def _get_or_create_data_contract(
        self,
        contract_name: str,
        version: str,
        status: str = "active",
        description: Optional[str] = None,
    ) -> int:
        """
        Get or create a data_contract record.

        Args:
            contract_name: Data contract name
            version: Contract version
            status: Contract status (default: "active")
            description: Optional description

        Returns:
            Data contract ID
        """
        self._require_connection()
        conn = self._get_connection()

        with conn.cursor() as cur:
            # Try to get existing data contract
            cur.execute(
                f"""
                SELECT id FROM {self._table_name("data_contracts")}
                WHERE name = %s AND version = %s
                """,
                (contract_name, version),
            )

            row = cur.fetchone()
            if row:
                return row[0]

            # Create new data contract (schema_id will be set later)
            cur.execute(
                f"""
                INSERT INTO {self._table_name("data_contracts")} 
                    (id, name, version, status, description)
                VALUES (gen_random_uuid(), %s, %s, %s, %s)
                RETURNING id
                """,
                (contract_name, version, status, description),
            )

            data_contract_id = cur.fetchone()[0]
            conn.commit()
            return data_contract_id

    def store_schema(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        version: str,
    ) -> str:
        """
        Store a schema in PostgreSQL.

        Args:
            schema_name: Name/identifier for the schema (used as data_contract name)
            schema: JSON Schema dictionary
            version: Required version string (must match schema["version"] if present)

        Returns:
            Schema ID as string

        Raises:
            ValueError: If version is missing or doesn't match schema version
        """
        self._require_connection()
        conn = self._get_connection()

        # Ensure schema has version
        if "version" not in schema:
            schema = dict(schema)
            schema["version"] = version
        elif schema.get("version") != version:
            raise ValueError(
                f"Version mismatch: provided version '{version}' does not match "
                f"schema version '{schema.get('version')}'"
            )

        # Get or create data contract
        data_contract_id = self._get_or_create_data_contract(
            contract_name=schema_name,
            version=version,
            description=schema.get("description"),
        )

        # Get title from schema or use schema_name
        title = schema.get("title") or schema_name

        with conn.cursor() as cur:
            # Check if schema already exists for this data_contract_id and version
            cur.execute(
                f"""
                SELECT id FROM {self._table_name("schemas")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            existing = cur.fetchone()

            if existing:
                # Update existing schema
                schema_id = existing[0]
                cur.execute(
                    f"""
                    UPDATE {self._table_name("schemas")}
                    SET schema_data = %s,
                        title = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (json.dumps(schema), title, schema_id),
                )
            else:
                # Insert new schema
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name("schemas")} 
                        (id, title, data_contract_id, version, schema_data)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (title, data_contract_id, version, json.dumps(schema)),
                )
                schema_id = cur.fetchone()[0]

            # Update data_contract with schema_id
            cur.execute(
                f"""
                UPDATE {self._table_name("data_contracts")}
                SET schema_id = %s, schema_version = %s
                WHERE id = %s
                """,
                (schema_id, version, data_contract_id),
            )

            conn.commit()
            return str(schema_id)

    def get_schema(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a schema by ID and optional version.

        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, returns latest version)

        Returns:
            Schema dictionary with version included, or None if not found
        """
        self._require_connection()
        conn = self._get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(
                    f"""
                    SELECT schema_data, version 
                    FROM {self._table_name("schemas")}
                    WHERE id = %s AND version = %s
                    """,
                    (schema_id, version),
                )
            else:
                cur.execute(
                    f"""
                    SELECT schema_data, version 
                    FROM {self._table_name("schemas")}
                    WHERE id = %s 
                    ORDER BY version DESC 
                    LIMIT 1
                    """,
                    (schema_id,),
                )

            row = cur.fetchone()
            if not row:
                return None

            schema_data = self._parse_jsonb(row["schema_data"])
            stored_version = row.get("version")

            # Ensure schema has version
            if "version" not in schema_data:
                schema_data = dict(schema_data)
                schema_data["version"] = stored_version or "1.0.0"

            return schema_data

    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all stored schemas."""
        self._require_connection()
        conn = self._get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT s.id, s.title, s.version, dc.name as data_contract_name
                FROM {self._table_name("schemas")} s
                LEFT JOIN {self._table_name("data_contracts")} dc 
                    ON s.data_contract_id = dc.id
                ORDER BY s.title, s.version
                """
            )
            return [
                {
                    "id": str(row["id"]),
                    "name": row.get("data_contract_name") or row.get("title"),
                    "title": row.get("title"),
                    "version": row.get("version"),
                }
                for row in cur.fetchall()
            ]

    # ============================================================================
    # Metadata Operations
    # ============================================================================

    def store_metadata(
        self,
        schema_id: str,
        metadata: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store additional metadata.

        Args:
            schema_id: Schema identifier
            metadata: Metadata dictionary
            version: Optional version string (if None, uses schema version)

        Returns:
            Metadata record ID
        """
        self._require_connection()
        conn = self._get_connection()

        # Get data_contract_id, name, and version from schema/data_contract
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT s.data_contract_id, s.version, dc.name as data_contract_name
                FROM {self._table_name("schemas")} s
                JOIN {self._table_name("data_contracts")} dc 
                    ON s.data_contract_id = dc.id
                WHERE s.id = %s
                """,
                (schema_id,),
            )

            row = cur.fetchone()
            if not row:
                raise ValueError(f"Schema not found: {schema_id}")

            data_contract_id = row["data_contract_id"]
            schema_version = row["version"]
            data_contract_name = row["data_contract_name"]

            # Use provided version or schema version
            if not version:
                version = schema_version

        # Extract metadata fields
        title = metadata.get("title") or f"Metadata for {schema_id}"
        status = metadata.get("status", "active")
        description = metadata.get("description")
        governance_rules = metadata.get("governance_rules")

        self._require_connection()
        conn = self._get_connection()
        with conn.cursor() as cur:
            # Check if metadata_record already exists
            cur.execute(
                f"""
                SELECT id FROM {self._table_name("metadata_records")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            existing = cur.fetchone()

            if existing:
                # Update existing metadata_record
                metadata_id = existing[0]
                cur.execute(
                    f"""
                    UPDATE {self._table_name("metadata_records")}
                    SET title = %s,
                        status = %s,
                        description = %s,
                        governance_rules = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        title,
                        status,
                        description,
                        json.dumps(governance_rules) if governance_rules else None,
                        metadata_id,
                    ),
                )
            else:
                # Insert new metadata_record
                # Note: 'data_contract' column exists in DB for backward compatibility
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name("metadata_records")} (
                        id, title, data_contract_id, version, status, description, 
                        governance_rules, data_contract
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        title,
                        data_contract_id,
                        version,
                        status,
                        description,
                        json.dumps(governance_rules) if governance_rules else None,
                        data_contract_name,
                    ),
                )
                metadata_id = cur.fetchone()[0]

            # Update data_contract with metadata_record_id
            cur.execute(
                f"""
                UPDATE {self._table_name("data_contracts")}
                SET metadata_record_id = %s, metadata_version = %s
                WHERE id = %s
                """,
                (metadata_id, version, data_contract_id),
            )
            conn.commit()

            conn.commit()
            return str(metadata_id)

    def get_metadata(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a schema.

        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, uses latest version)

        Returns:
            Metadata dictionary or None if not found
        """
        self._require_connection()
        conn = self._get_connection()

        # Get metadata_record via schema -> data_contract
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if version:
                cur.execute(
                    f"""
                    SELECT mr.*
                    FROM {self._table_name("metadata_records")} mr
                    JOIN {self._table_name("schemas")} s 
                        ON mr.data_contract_id = s.data_contract_id
                    WHERE s.id = %s AND mr.version = %s
                    ORDER BY mr.version DESC
                    LIMIT 1
                    """,
                    (schema_id, version),
                )
            else:
                cur.execute(
                    f"""
                    SELECT mr.*
                    FROM {self._table_name("metadata_records")} mr
                    JOIN {self._table_name("schemas")} s 
                        ON mr.data_contract_id = s.data_contract_id
                    WHERE s.id = %s
                    ORDER BY mr.version DESC
                    LIMIT 1
                    """,
                    (schema_id,),
                )

            row = cur.fetchone()
            if not row:
                return None

            # Reconstruct metadata dictionary
            metadata = {
                "title": row.get("title"),
                "status": row.get("status"),
                "description": row.get("description"),
                "version": row.get("version"),
            }

            # Add JSON fields
            if row.get("governance_rules"):
                metadata["governance_rules"] = self._parse_jsonb(
                    row["governance_rules"]
                )

            return metadata

    # ============================================================================
    # Coercion Rules Operations
    # ============================================================================

    def store_coercion_rules(
        self,
        schema_id: str,
        coercion_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store coercion rules for a schema.

        Args:
            schema_id: Schema identifier
            coercion_rules: Dictionary of coercion rules
            version: Optional version string (if None, uses schema version)

        Returns:
            Rule ID or identifier
        """
        self._require_connection()
        conn = self._get_connection()

        # Get data_contract_id, name, and version from schema/data_contract
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT s.data_contract_id, s.version, s.title, dc.name as data_contract_name
                FROM {self._table_name("schemas")} s
                JOIN {self._table_name("data_contracts")} dc 
                    ON s.data_contract_id = dc.id
                WHERE s.id = %s
                """,
                (schema_id,),
            )

            row = cur.fetchone()
            if not row:
                raise ValueError(f"Schema not found: {schema_id}")

            data_contract_id = row["data_contract_id"]
            schema_version = row["version"]
            schema_title = row["title"]
            data_contract_name = row["data_contract_name"]

            # Use provided version or schema version
            if not version:
                version = schema_version

        # Create title for coercion rules
        title = f"{schema_title} Coercion Rules"

        self._require_connection()
        conn = self._get_connection()
        with conn.cursor() as cur:
            # Check if coercion_rules already exists
            cur.execute(
                f"""
                SELECT id FROM {self._table_name("coercion_rules")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            existing = cur.fetchone()

            if existing:
                # Update existing coercion_rules
                rule_id = existing[0]
                # Note: 'data_contract' column exists in DB for backward compatibility
                cur.execute(
                    f"""
                    UPDATE {self._table_name("coercion_rules")}
                    SET rules = %s,
                        title = %s,
                        schema_id = %s,
                        data_contract = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        json.dumps(coercion_rules),
                        title,
                        schema_id,
                        data_contract_name,
                        rule_id,
                    ),
                )
            else:
                # Insert new coercion_rules
                # Note: 'data_contract' column exists in DB for backward compatibility
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name("coercion_rules")} (
                        id, title, data_contract_id, version, rules, schema_id, data_contract
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        title,
                        data_contract_id,
                        version,
                        json.dumps(coercion_rules),
                        schema_id,
                        data_contract_name,
                    ),
                )
                rule_id = cur.fetchone()[0]

            # Update data_contract with coercion_rules_id
            cur.execute(
                f"""
                UPDATE {self._table_name("data_contracts")}
                SET coercion_rules_id = %s, coercion_rules_version = %s
                WHERE id = %s
                """,
                (rule_id, version, data_contract_id),
            )
            conn.commit()

            conn.commit()
            return f"coercion:{schema_id}" + (f":{version}" if version else "")

    def get_coercion_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve coercion rules for a schema.

        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, uses schema version)

        Returns:
            Dictionary of coercion rules, or None if not found
        """
        self._require_connection()
        conn = self._get_connection()

        # Get data_contract_id from schema
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT data_contract_id, version
                FROM {self._table_name("schemas")}
                WHERE id = %s
                """,
                (schema_id,),
            )

            row = cur.fetchone()
            if not row:
                return None

            data_contract_id = row["data_contract_id"]
            schema_version = row["version"]

            # Use provided version or schema version
            if not version:
                version = schema_version

            # Get coercion rules
            cur.execute(
                f"""
                SELECT rules
                FROM {self._table_name("coercion_rules")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            row = cur.fetchone()
            if not row:
                return None

            return self._parse_jsonb(row["rules"])

    # ============================================================================
    # Validation Rules Operations
    # ============================================================================

    def store_validation_rules(
        self,
        schema_id: str,
        validation_rules: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Store validation rules for a schema.

        Args:
            schema_id: Schema identifier
            validation_rules: Dictionary of validation rules
            version: Optional version string (if None, uses schema version)

        Returns:
            Rule ID or identifier
        """
        self._require_connection()
        conn = self._get_connection()

        # Get data_contract_id, name, and version from schema/data_contract
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT s.data_contract_id, s.version, s.title, dc.name as data_contract_name
                FROM {self._table_name("schemas")} s
                JOIN {self._table_name("data_contracts")} dc 
                    ON s.data_contract_id = dc.id
                WHERE s.id = %s
                """,
                (schema_id,),
            )

            row = cur.fetchone()
            if not row:
                raise ValueError(f"Schema not found: {schema_id}")

            data_contract_id = row["data_contract_id"]
            schema_version = row["version"]
            schema_title = row["title"]
            data_contract_name = row["data_contract_name"]

            # Use provided version or schema version
            if not version:
                version = schema_version

        # Create title for validation rules
        title = f"{schema_title} Validation Rules"

        self._require_connection()
        conn = self._get_connection()
        with conn.cursor() as cur:
            # Check if validation_rules already exists
            cur.execute(
                f"""
                SELECT id FROM {self._table_name("validation_rules")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            existing = cur.fetchone()

            if existing:
                # Update existing validation_rules
                rule_id = existing[0]
                # Note: 'data_contract' column exists in DB for backward compatibility
                cur.execute(
                    f"""
                    UPDATE {self._table_name("validation_rules")}
                    SET rules = %s,
                        title = %s,
                        schema_id = %s,
                        data_contract = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        json.dumps(validation_rules),
                        title,
                        schema_id,
                        data_contract_name,
                        rule_id,
                    ),
                )
            else:
                # Insert new validation_rules
                # Note: 'data_contract' column exists in DB for backward compatibility
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name("validation_rules")} (
                        id, title, data_contract_id, version, rules, schema_id, data_contract
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        title,
                        data_contract_id,
                        version,
                        json.dumps(validation_rules),
                        schema_id,
                        data_contract_name,
                    ),
                )
                rule_id = cur.fetchone()[0]

            # Update data_contract with validation_rules_id
            cur.execute(
                f"""
                UPDATE {self._table_name("data_contracts")}
                SET validation_rules_id = %s, validation_rules_version = %s
                WHERE id = %s
                """,
                (rule_id, version, data_contract_id),
            )
            conn.commit()

            conn.commit()
            return f"validation:{schema_id}" + (f":{version}" if version else "")

    def get_validation_rules(
        self, schema_id: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve validation rules for a schema.

        Args:
            schema_id: Schema identifier
            version: Optional version string (if None, uses schema version)

        Returns:
            Dictionary of validation rules, or None if not found
        """
        self._require_connection()
        conn = self._get_connection()

        # Get data_contract_id from schema
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT data_contract_id, version
                FROM {self._table_name("schemas")}
                WHERE id = %s
                """,
                (schema_id,),
            )

            row = cur.fetchone()
            if not row:
                return None

            data_contract_id = row["data_contract_id"]
            schema_version = row["version"]

            # Use provided version or schema version
            if not version:
                version = schema_version

            # Get validation rules
            cur.execute(
                f"""
                SELECT rules
                FROM {self._table_name("validation_rules")}
                WHERE data_contract_id = %s AND version = %s
                """,
                (data_contract_id, version),
            )

            row = cur.fetchone()
            if not row:
                return None

            return self._parse_jsonb(row["rules"])
