import json
from .storage import ConfigStorageBase


class DBConfigStorage(ConfigStorageBase):
    @staticmethod
    def create_table_if_needed(engine, table_name="app_configs"):
        from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData, func, Index
        metadata = MetaData()
        if not engine.dialect.has_table(engine, table_name):
            t = Table(
                table_name, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('service_name', String(128), nullable=False, index=True),
                Column('config_data', Text, nullable=False),
                Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
            )
            Index(f"ix_{table_name}_service_name", t.c.service_name)
            metadata.create_all(bind=engine, checkfirst=True)

    def __init__(self, session_factory, table, key_column: str, value_column: str, config_id=None, auto_reload: bool = False, service_name: str = None, updated_at_column: str = "updated_at", engine=None):
        super().__init__(auto_reload=auto_reload)
        self.session_factory = session_factory
        self.table = table
        self.key_column = key_column
        self.value_column = value_column
        self.config_id = config_id
        self.service_name = service_name
        self.updated_at_column = updated_at_column
        self._last_update = None
        if engine:
            self.create_table_if_needed(engine, getattr(table, '__tablename__', 'app_configs'))

    def load(self) -> dict:
        session = self.session_factory()
        try:
            q = session.query(self.table)
            if self.config_id is not None and hasattr(self.table, 'id'):
                q = q.filter(self.table.id == self.config_id)
            if self.service_name and hasattr(self.table, "service_name"):
                q = q.filter(self.table.service_name == self.service_name)
            row = q.order_by(getattr(self.table, self.updated_at_column).desc()).first()
            if not row:
                return {}
            if hasattr(row, self.updated_at_column):
                self._last_update = getattr(row, self.updated_at_column)
            value = getattr(row, self.value_column)
            return json.loads(value)
        finally:
            session.close()

    def save(self, data: dict):
        session = self.session_factory()
        try:
            q = session.query(self.table)
            if self.config_id is not None and hasattr(self.table, 'id'):
                q = q.filter(self.table.id == self.config_id)
            if self.service_name and hasattr(self.table, "service_name"):
                q = q.filter(self.table.service_name == self.service_name)
            obj = q.first()
            value = json.dumps(data, ensure_ascii=False)
            if obj:
                setattr(obj, self.value_column, value)
            else:
                values = {self.key_column: self.service_name if self.key_column == 'service_name' else None,
                          self.value_column: value}
                obj = self.table(**values)
                session.add(obj)
            session.commit()
            if hasattr(obj, self.updated_at_column):
                self._last_update = getattr(obj, self.updated_at_column)
        finally:
            session.close()

    def has_changed(self) -> bool:
        if not self.auto_reload:
            return False
        session = self.session_factory()
        try:
            q = session.query(self.table)
            if self.service_name and hasattr(self.table, "service_name"):
                q = q.filter(self.table.service_name == self.service_name)
            row = q.order_by(getattr(self.table, self.updated_at_column).desc()).first()
            if not row or not hasattr(row, self.updated_at_column):
                return False
            cur_update = getattr(row, self.updated_at_column)
            changed = cur_update != self._last_update
            if changed:
                self._last_update = cur_update
            return changed
        finally:
            session.close()
