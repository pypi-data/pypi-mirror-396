from unittest import TestCase
from unittest.mock import patch, MagicMock
from eaasy.domain.database import *
from sqlalchemy.exc import IntegrityError
import os
import eaasy.domain.database as database


class TestSessionManagement(TestCase):
    def setUp(self):
        self._orig_engine = database._engine
        self._orig_session_factory = database._session_factory
        database._engine = None
        database._session_factory = None

    def tearDown(self):
        database._engine = self._orig_engine
        database._session_factory = self._orig_session_factory
    @patch.dict(os.environ, {'POSTGRES_URI': 'postgresql://user@ip:0/db'}, clear=True)
    @patch('eaasy.domain.database.scoped_session')
    @patch('eaasy.domain.database.sessionmaker')
    @patch('eaasy.domain.database.create_engine')
    def test_get_session_uses_singleton_pattern(self, mock_create_engine, mock_sessionmaker, mock_scoped_session):
        fake_engine = MagicMock(name='engine')
        fake_scoped = MagicMock(name='scoped_session')
        mock_create_engine.return_value = fake_engine
        mock_sessionmaker.return_value = MagicMock(name='session_factory')
        mock_scoped_session.return_value = fake_scoped

        session_manager_1 = Common.get_session()
        session_manager_2 = Common.get_session()

        self.assertIs(session_manager_1.session, fake_scoped)
        self.assertIs(session_manager_2.session, fake_scoped)
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(bind=fake_engine)
        mock_scoped_session.assert_called_once_with(mock_sessionmaker.return_value)


class MockQuery:
    def __init__(self, return_value):
        self.return_value = return_value

    def all(self):
        return self.return_value

    def get(self, *args, **kwargs):
        return self.return_value

    def first(self):
        return self.return_value

    def filter_by(self, *args, **kwargs):
        return self
    
    def order_by(self, *args, **kwargs):
        return self


class MockSession(MagicMock):
    def query(self, *args, **kwargs):
        return MockQuery(return_value=self.return_value)

    def commit(self):
        if self.exc_commit:
            raise self.exc_commit(*self.exc_args)


@patch.dict('os.environ', {'POSTGRES_URI': 'postgresql://user@ip:0/db'}, clear=True)
@patch('sqlalchemy.create_engine')
@patch('eaasy.domain.database.Common.get_session')
class TestBaseTable(TestCase):
    def test_querying_all_returns_empty_list(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=[]) # type: ignore

        # Act
        result = BaseEntity.get_all()

        # Assert
        self.assertEqual(result, [])

    def test_querying_all_returns_list_of_objects(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=[1, 2, 3])

        # Act
        result = BaseEntity.get_all()

        # Assert
        self.assertEqual(result, [1, 2, 3])

    def test_querying_by_id_raises_not_found(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=None)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.get_by_id(1)

        self.assertEqual(context.exception.args[0]['status_code'], 404)
        self.assertEqual(
            context.exception.args[0]['message'], r"BaseEntity with {'id': 1} not found")

    def test_querying_by_id_returns_object(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=1)

        # Act
        result = BaseEntity.get_by_id(1)

        # Assert
        self.assertEqual(result, 1)

    def test_creating_object_raises_bad_request_when_field_is_null(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=None,
            exc_commit=IntegrityError,
            exc_args=(None, None, 'not-null "id"')
            )

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.create(id=None)

        self.assertEqual(context.exception.args[0]['status_code'], 400)
        self.assertEqual(
            context.exception.args[0]['message'], "id cannot be null")
        
    def test_creating_object_raises_bad_request_when_foreign_key_not_found(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=None,
            exc_commit=IntegrityError,
            exc_args=(None, None, 'violates foreign key constraint ("id")=(1)')
            )

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.create(id=1)

        self.assertEqual(context.exception.args[0]['status_code'], 400)
        self.assertEqual(
            context.exception.args[0]['message'], "invalid foreign key: id with id 1 not found")

    def test_creating_object_raises_conflict_when_entity_already_exists(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=None,
            exc_commit=IntegrityError,
            exc_args=(None, None, "duplicate key|DETAIL:  details\n"))

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.create(id=1)

        self.assertEqual(context.exception.args[0]['status_code'], 409)
        self.assertEqual(
            context.exception.args[0]['message'], "BaseEntity details")

    def test_creating_object_raises_generic_failure_when_unknown_integrity_error_occurs(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=None,
            exc_commit=IntegrityError,
            exc_args=(None, None, 'unknown error'))

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.create(id=1)

        self.assertEqual(context.exception.args[0]['status_code'], 500)
        self.assertEqual(
            context.exception.args[0]['message'], "unknown error")

    def test_creating_object_raises_exception_on_error(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=None,
            exc_commit=Exception,
            exc_args=('exception', 'inner exception'))

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.create(id=1)

        self.assertEqual(context.exception.args[0]['status_code'], 500)
        self.assertEqual(
            context.exception.args[0]['message'], str(('exception', 'inner exception')))

    def test_creating_object_returns_object(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(
            return_value=1,
            exc_commit=None)

        # Act
        result = BaseEntity.create(id=1)

        # Assert
        self.assertEqual(result.id, 1)

    def test_updating_object_raises_not_found(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=None)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.update(1)

        self.assertEqual(context.exception.args[0]['status_code'], 404)
        self.assertEqual(
            context.exception.args[0]['message'], "BaseEntity with {'id': 1} not found")

    @patch('sqlalchemy.update') 
    def test_updating_object_raises_bad_request_when_field_is_null(self, mock_update, mock_get_session, *_):
        # Arrange
        missing_argument = 'missing_field'
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1})
        mock_update.side_effect = IntegrityError(None, None, f'not-null "{mock_update}"') # type: ignore

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.update(1, **{missing_argument: None})

        self.assertEqual(context.exception.args[0]['status_code'], 400)
        self.assertEqual(
            context.exception.args[0]['message'], f"{mock_update} cannot be null")
        
    @patch('sqlalchemy.update')
    def test_updating_object_raises_conflict_when_entity_already_exists(self, mock_update, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1})
        mock_update.side_effect = IntegrityError(None, None, 'duplicate key|DETAIL:  details\n') # type: ignore

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.update(1, **{'unique_property': 1})

        self.assertEqual(context.exception.args[0]['status_code'], 409)
        self.assertEqual(
            context.exception.args[0]['message'], "BaseEntity details")
        
    @patch('sqlalchemy.update')
    def test_updating_object_raises_generic_failure_when_unknown_integrity_error_occurs(self, mock_update, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1})
        mock_update.side_effect = Exception('unknown error')

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.update(1, **{'unique_property': 1})

        self.assertEqual(context.exception.args[0]['status_code'], 500)
        self.assertEqual(
            context.exception.args[0]['message'], "unknown error")
        
    @patch('sqlalchemy.update')
    def test_updating_object_returns_object(self, _, mock_get_session, *__):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1}, exc_commit=None)

        # Act
        result = BaseEntity.update(1, **{'any': 1})

        # Assert
        self.assertEqual(result['id'], 1)

    def test_deleting_object_raises_not_found(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value=None)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.delete(1)

        self.assertEqual(context.exception.args[0]['status_code'], 404)
        self.assertEqual(
            context.exception.args[0]['message'], "BaseEntity with {'id': 1} not found")
    
    def test_deleting_object_raises_exception_on_error(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1}, exc_commit=Exception, exc_args=('exception', 'inner exception'))

        # Act & Assert
        with self.assertRaises(Exception) as context:
            BaseEntity.delete(1)

        self.assertEqual(context.exception.args[0]['status_code'], 500)
        self.assertEqual(
            context.exception.args[0]['message'], str(('exception', 'inner exception')))
        
    def test_deleting_object_returns_success(self, mock_get_session, *_):
        # Arrange
        mock_get_session.return_value.__enter__.return_value = MockSession(return_value={'id': 1}, exc_commit=None)

        # Act
        result = BaseEntity.delete(1)

        # Assert
        self.assertIsNone(result)
