"""Logger tests, run against the real logger (no copies of its code)."""

import io
import json
import unittest
import warnings

import ft3

from ft3.loggers import lib

from .. import mocking

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to this file."""


def message_of(record: lib.logging.LogRecord) -> dict:
	"""The structured message a record carries."""

	return getattr(record, 'ft3_message')


class TestLogger(unittest.TestCase):
	"""Records carry the parsed, redacted message in every shape."""

	def setUp(self) -> None:
		self.log = ft3.log
		return super().setUp()

	def assertLogged(self, msg, level, method):
		expected = ft3.core.strings.utl.convert_for_repr(
			ft3.loggers.utl.parse_incoming_log_message(msg, level)
		)
		with self.assertLogs(self.log, level) as logger:
			method(msg)
		record = logger.records[0]
		self.assertEqual(message_of(record), expected)
		self.assertEqual(json.loads(record.msg), expected)
		return record

	def test_01_str(self):
		self.assertLogged('example', lib.logging.DEBUG, self.log.debug)

	def test_02_dict(self):
		self.assertLogged({'str': 'example', 'a': 2}, 20, self.log.info)

	def test_03_cls(self):
		self.assertLogged(mocking.examples.Pet, 30, self.log.warning)

	def test_04_object(self):
		pet = mocking.examples.Pet(id_='abc1234', name='Fido', type='dog')
		self.assertLogged(pet, lib.logging.ERROR, self.log.error)

	def test_05_array(self):
		self.assertLogged(['a', 1], lib.logging.INFO, self.log.info)

	def test_06_record_shaped_dicts_pass_through(self):
		msg = ft3.loggers.typ.LogRecord(content='test')
		self.assertEqual(
			msg, ft3.loggers.utl.parse_incoming_log_message(msg, 20)
		)
		msg = ('test',)
		self.assertEqual(
			ft3.loggers.typ.LogRecord(content=msg),
			ft3.loggers.utl.parse_incoming_log_message(msg, 20),
		)

	def test_07_printf_args_are_applied(self):
		with self.assertLogs(self.log, 20) as logger:
			self.log.info('a %s b %d', 'x', 2)
		self.assertEqual(message_of(logger.records[0])['content'], 'a x b 2')

	def test_08_caller_is_the_call_site(self):
		with self.assertLogs(self.log, 20) as logger:
			self.log.info('where')
		self.assertEqual(
			logger.records[0].funcName, 'test_08_caller_is_the_call_site'
		)

	def test_09_invalid_type_raises(self):
		with self.assertNoLogs(self.log):
			self.assertRaises(
				ft3.loggers.exc.InvalidLogMessageTypeError,
				lambda: self.log.info(42),
			)

	def test_10_level_for(self):
		self.assertEqual(ft3.loggers.obj.level_for('debug'), 10)
		self.assertEqual(ft3.loggers.obj.level_for('TRACE'), 20)


class TestFormatter(unittest.TestCase):
	"""Every emitted line is a valid JSON document."""

	def setUp(self) -> None:
		self.log = ft3.log
		return super().setUp()

	def test_01_envelope(self):
		with self.assertLogs(self.log, 20) as logger:
			self.log.info({'a': 1})
		line = ft3.loggers.Formatter(pretty=False).format(logger.records[0])
		self.assertNotIn('\n', line)
		envelope = json.loads(line)
		self.assertEqual(envelope['level'], 'INFO')
		self.assertEqual(envelope['logger'], 'ft3')
		self.assertTrue(envelope['timestamp'].endswith('Z'))
		self.assertEqual(envelope['message'], {'content': {'a': 1}})

	def test_02_pretty(self):
		with self.assertLogs(self.log, 20) as logger:
			self.log.info('x')
		line = ft3.loggers.Formatter(pretty=True).format(logger.records[0])
		self.assertIn('\n', line)
		self.assertEqual(json.loads(line)['message'], {'content': 'x'})

	def test_03_pretty_from_env_setting(self):
		ft3.loggers.cfg.Constants.LOG_FORMAT = 'pretty'
		try:
			with self.assertLogs(self.log, 20) as logger:
				self.log.info('x')
			self.assertIn('\n', logger.records[0].msg)
			self.assertIn(
				'\n', ft3.loggers.Formatter().format(logger.records[0])
			)
		finally:
			ft3.loggers.cfg.Constants.LOG_FORMAT = 'json'

	def test_04_foreign_records_are_wrapped(self):
		record = lib.logging.LogRecord(
			'other', 20, 'x.py', 1, 'hello %s', ('world',), None
		)
		envelope = json.loads(
			ft3.loggers.Formatter(pretty=False).format(record)
		)
		self.assertEqual(envelope['logger'], 'other')
		self.assertEqual(envelope['message'], {'content': 'hello world'})

	def test_05_root_handler_uses_formatter(self):
		formatters = [h.formatter for h in lib.logging.getLogger().handlers]
		self.assertTrue(
			any(isinstance(f, ft3.loggers.Formatter) for f in formatters)
		)


class TestPrints(unittest.TestCase):
	"""`print()` becomes an INFO record carrying the printed text."""

	def setUp(self) -> None:
		self.log = ft3.log
		return super().setUp()

	def test_01_print_is_logged(self):
		with self.assertLogs(self.log, 20) as logger:
			print('hello', 'world', sep='-')
		message = message_of(logger.records[0])
		self.assertEqual(message['printed'], 'hello-world')
		self.assertIn('print()', message['content'])
		self.assertEqual(logger.records[0].funcName, 'test_01_print_is_logged')

	def test_02_print_to_file_is_untouched(self):
		buffer = io.StringIO()
		with self.assertNoLogs(self.log):
			print('kept', file=buffer)
		self.assertEqual(buffer.getvalue(), 'kept\n')

	def test_03_repeated_prints_are_all_logged(self):
		with self.assertLogs(self.log, 20) as logger:
			print('same')
			print('same')
		self.assertEqual(len(logger.records), 2)


class TestWarnings(unittest.TestCase):
	"""`warnings.warn` is captured as a WARNING record, once."""

	def test_01_captured_warning_keeps_only_the_message(self):
		with self.assertLogs(ft3.log, 30) as logger:
			warnings.warn('careful now', stacklevel=1)
		self.assertEqual(
			message_of(logger.records[0])['content'], 'careful now'
		)

	def test_02_parse_captured_warning(self):
		text = 'x.py:12: UserWarning: the message: with colon\n  src\n'
		self.assertEqual(
			ft3.loggers.utl.parse_captured_warning(text),
			'the message: with colon',
		)
		self.assertEqual(
			ft3.loggers.utl.parse_captured_warning('bare'), 'bare'
		)


class TestTracebacks(unittest.TestCase):
	"""Tracebacks are attached whole, never truncated."""

	def setUp(self) -> None:
		ft3.loggers.cfg.Constants.LOG_TRACEBACK = True
		return super().setUp()

	def deep(self, n: int) -> None:
		if n == 0:
			raise ValueError('bottom')
		self.deep(n - 1)

	def test_01_error_inside_except_attaches_full_traceback(self):
		with self.assertLogs(ft3.log, 40) as logger:
			try:
				self.deep(30)
			except ValueError:
				ft3.log.error('boom')
		traceback = message_of(logger.records[0])['traceback']
		cutoff = ft3.core.strings.cfg.Constants.CUTOFF_LEN
		self.assertGreater(len(traceback), cutoff)
		self.assertEqual(traceback[-1], 'ValueError: bottom')
		self.assertNotIn(
			ft3.core.strings.cfg.Constants.M_LINE_TOKEN, traceback
		)
		self.assertEqual(
			json.loads(logger.records[0].msg)['traceback'], traceback
		)

	def test_02_explicit_exception_and_tuple(self):
		try:
			1 / 0
		except ZeroDivisionError as error:
			caught = error
		with self.assertLogs(ft3.log, 40) as logger:
			ft3.log.error('a', exc_info=caught)
			ft3.log.error('b', exc_info=(type(caught), caught, None))
		for record in logger.records:
			self.assertIn(
				'ZeroDivisionError', message_of(record)['traceback'][-1]
			)

	def test_03_exc_info_false_suppresses(self):
		with self.assertLogs(ft3.log, 40) as logger:
			try:
				1 / 0
			except ZeroDivisionError:
				ft3.log.error('quiet', exc_info=False)
		self.assertNotIn('traceback', message_of(logger.records[0]))

	def test_04_below_error_has_no_traceback(self):
		with self.assertLogs(ft3.log, 10) as logger:
			try:
				1 / 0
			except ZeroDivisionError as error:
				ft3.log.debug('x', exc_info=error)
		self.assertNotIn('traceback', message_of(logger.records[0]))

	def test_05_keyboard_interrupt_is_not_attached(self):
		with self.assertLogs(ft3.log, 40) as logger:
			try:
				raise KeyboardInterrupt
			except KeyboardInterrupt:
				ft3.log.error('stop')
		self.assertNotIn('traceback', message_of(logger.records[0]))

	def test_06_disabled_by_setting(self):
		ft3.loggers.cfg.Constants.LOG_TRACEBACK = False
		try:
			with self.assertLogs(ft3.log, 40) as logger:
				try:
					1 / 0
				except ZeroDivisionError:
					ft3.log.error('x')
			self.assertNotIn('traceback', message_of(logger.records[0]))
		finally:
			ft3.loggers.cfg.Constants.LOG_TRACEBACK = True


class TestRedaction(unittest.TestCase):
	"""Sensitive values never reach the log stream."""

	def logged(self, msg) -> str:
		with self.assertLogs(ft3.log, 20) as logger:
			ft3.log.info(msg)
		return logger.records[0].msg

	def test_01_key_patterns(self):
		for key in ('apiKey', 'password', 'accessToken', 'client_secret'):
			with self.subTest(key=key):
				self.assertIn('REDACTED', self.logged({key: 'hunter2'}))
		self.assertNotIn('REDACTED', self.logged({'token_count': 'x'}))

	def test_02_value_patterns(self):
		values = {
			'AKIARJFBAG3EGHFG2FPN': 'AWS_ACCESS_KEY_ID',
			'postgres://user:pw@host/db': 'CONN_STRING_PASSWORD',
			'4111111111111111': 'CREDIT_CARD',
			'123-45-6789': 'SSN',
		}
		for value, ref in values.items():
			with self.subTest(value=value):
				self.assertIn(ref, self.logged({'note': value}))
		self.assertIn(
			'postgres://user:[ REDACTED :: CONN_STRING_PASSWORD ]@host/db',
			self.logged({'note': 'postgres://user:pw@host/db'}),
		)

	def test_02b_allowlisted_keys_are_kept(self):
		ft3.core.strings.cfg.Constants.REDACT_ALLOW = ('arena_tokens',)
		try:
			self.assertNotIn('REDACTED', self.logged({'arena_tokens': '5'}))
			self.assertIn('REDACTED', self.logged({'device_token': '5'}))
		finally:
			ft3.core.strings.cfg.Constants.REDACT_ALLOW = ()

	def test_03_all_string_lists_are_redacted(self):
		self.assertIn('REDACTED', self.logged(['AKIARJFBAG3EGHFG2FPN']))
		self.assertIn('step_one', self.logged(['step_one', 'hero-42']))

	def test_04_long_strings_are_wrapped(self):
		self.assertIn(
			ft3.core.strings.cfg.Constants.M_LINE_TOKEN,
			self.logged({'longString': 'ABCDEFG' * 1024}),
		)
