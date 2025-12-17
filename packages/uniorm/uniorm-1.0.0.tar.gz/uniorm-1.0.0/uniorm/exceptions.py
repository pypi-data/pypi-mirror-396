"""Custom exceptions for UniORM"""


class UniORMException(Exception):
    """Base exception for UniORM"""
    pass


class DatabaseError(UniORMException):
    """Database operation error"""
    pass


class IntegrityError(DatabaseError):
    """Data integrity error (e.g., unique constraint violation)"""
    pass


class DoesNotExist(UniORMException):
    """Object does not exist in database"""
    pass


class MultipleObjectsReturned(UniORMException):
    """Multiple objects returned when one was expected"""
    pass


class ConfigurationError(UniORMException):
    """Configuration error"""
    pass


class MigrationError(UniORMException):
    """Migration error"""
    pass