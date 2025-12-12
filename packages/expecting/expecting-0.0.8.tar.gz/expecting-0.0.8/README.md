# expecting

Elegant assertions library.

This is currently a work in progress.

* [`expecting.dict`](#expectingdict): Dictionary assertions, combined with other assertions makes it easier to verify complex dictionary schemas.
* [`expecting.list`](./src/expecting/dict): Utility assertions, like order agnostic comparisons.
* [`expecting.enum`](./src/expecting/enum): Enum related assertions, checking values, names, or instances.
* [`expecting.number`](./src/expecting/number): Simple number comparisons, the small building blocks for more complex structured data checking.
* [`expecting.string`](./src/expecting/string): A variety of formats like date and time, URL, UUID.


## Installation options

```bash
pip install expecting
```
```bash
poetry add expecting --group dev
```

## Usage

Expecting consists of a set of assertion objects that can be used with `assert` statements in a clear, readable way.
Most common assertion will be covered under a structured set of modules, following an intuitive naming schema:

```python
import expecting

assert '2023-10-11' == expecting.string.datetime.iso8601_day()
```

Here, the `expcting.string.datetime` module introduces a handful of factory methods for asserting that the value is a
string representing a date and time format.

It's specially useful with [pytest](https://docs.pytest.org/)  and its amazing error messages, where an assertion
failure message would look something like:

```text
string/test_datetime.py:7 (test_iso8601_full_matches[2023/10/11 13:01:10])
'2023/10/11 13:01:10' != ~= <datetime as "%Y-%m-%dT%H:%M:%S.%f%z">

Expected :~= <datetime as "%Y-%m-%dT%H:%M:%S.%f%z">
Actual   :'2023/10/11 13:01:10'
<Click to see difference>

datetime_str = '2023/10/11 13:01:10'

    @pytest.mark.parametrize(
        'datetime_str',
        (
            '2023/10/11 13:01:10',
        )
    )
    def test_iso8601_full_matches(datetime_str: str):
>       assert datetime_str == expecting.string.datetime.iso8601_full()
E       assert '2023/10/11 13:01:10' == ~= <datetime as "%Y-%m-%dT%H:%M:%S.%f%z">
...
```

The `~=` symbol prefixing the expected value is used denote this value is an "expecting object".

## Contributing

Feel free to create issues or merge requests with any improvement or fix you might find useful.

## API reference

* [`expecting.dict`](#expectingdict)
  * [`containing`](#expectingdictcontaining)
* [`expecting.enum`](#expectingenum)
  * [`any_value_of`](#expectingenumany_value_of)
* [`expecting.list`](#expectinglist)
  * [`containing`](#expectinglistcontaining)
  * [`unordered`](#expectinglistunordered)
* [`expecting.number`](#expectingnumber)
  * [`expecting.number.any`](#expectingnumberany)
  * [`expecting.number.ge`](#expectingnumberge)
  * [`expecting.number.le`](#expectingnumberle)
  * [`expecting.number.gt`](#expectingnumbergt)
  * [`expecting.number.lt`](#expectingnumberlt)
  * [`expecting.number.eq`](#expectingnumbereq)
  * [`expecting.number.ne`](#expectingnumberne)
* [`expecting.string`](#expectingstring)
  * [`expecting.string.datetime`](#expectingstringdatetime)
    * [`expecting.string.datetime.iso8601_full`](#expectingstringdatetimeiso8601_full)
    * [`expecting.string.datetime.iso8601_millisecond`](#expectingstringdatetimeiso8601_millisecond)
    * [`expecting.string.datetime.iso8601_second`](#expectingstringdatetimeiso8601_second)
    * [`expecting.string.datetime.iso8601_minute`](#expectingstringdatetimeiso8601_minute)
    * [`expecting.string.datetime.iso8601_hour`](#expectingstringdatetimeiso8601_hour)
    * [`expecting.string.datetime.iso8601_day`](#expectingstringdatetimeiso8601_day)
    * [`expecting.string.datetime.iso8601_month`](#expectingstringdatetimeiso8601_month)
    * [`expecting.string.datetime.iso8601_year`](#expectingstringdatetimeiso8601_year)
  * [`expecting.string.url`](#expectingstringurl)
    * [`expecting.string.url.with_scheme`](#expectingstringurlwith_scheme)
    * [`expecting.string.url.with_netloc`](#expectingstringurlwith_netloc)
    * [`expecting.string.url.with_path`](#expectingstringurlwith_path)
    * [`expecting.string.url.with_query`](#expectingstringurlwith_query)
    * [`expecting.string.url.with_fragment`](#expectingstringurlwith_fragment)
    * [`expecting.string.url.with_components`](#expectingstringurlwith_components)
    * [`expecting.string.url.any`](#expectingstringurlany)
  * [`expecting.string.uuid`](#expectingstringuuid)
    * [`expecting.string.uuid.v1`](#expectingstringuuidv1)
    * [`expecting.string.uuid.v3`](#expectingstringuuidv3)
    * [`expecting.string.uuid.v4`](#expectingstringuuidv4)
    * [`expecting.string.uuid.v5`](#expectingstringuuidv5)
    * [`expecting.string.uuid.hex`](#expectingstringuuidhex)

## `expecting.dict`

### `expecting.dict.containing`

Asserts that a dictionary contains a sub-dictionary.

```python
import expecting

current = {
    'color': 'yellow',
    'positions': [(1, 1), (2, 3), (4, 2)],
}
assert current == expecting.dict.containing({
    'positions': expecting.list.containing([(2, 3)]),
    'color': 'yellow',
})
```

## `expecting.enum`

### `expecting.enum.any_value_of`

Asserts that a value represents a specific enum.

```python
import expecting
from enum import Enum


class AnyEnum(str, Enum):
    OK = 'OK'

assert 'OK' == expecting.enum.any_value_of(AnyEnum)
assert 'NOK' != expecting.enum.any_value_of(AnyEnum)
```

## `expecting.list`

### `expecting.list.containing`

Asserts that a list contains a sub-list. Order is important.

```python
import expecting

current = [1, 2, 3]
assert current == expecting.list.containing([2, 3])
```


### `expecting.list.unordered`

Asserts that a list contains all the values, disregarding their order.


```python
import expecting

current = [1, 2, 3]

assert current == expecting.list.unordered([3, 1, 2])
```

## `expecting.number`

Disclaimer: of course writing `assert a >= 1` is much easier and should be the preferred way to.

The functions under this namespace are intended for combined usage with other expecting objects for complex schema validations.

### `expecting.number.any`

Asserts any type of number.

```python
import expecting.number


assert 1 == expecting.number.any()
assert 0 == expecting.number.any()
assert -1.4 == expecting.number.any()
assert 'inf' == expecting.number.any()
```

### `expecting.number.ge`

Asserts number is greater than or equal to (>=) given value.

```python
import expecting

assert 10 == expecting.number.ge(10)
```

### `expecting.number.le`

Asserts number is lesser than or equal to (<=) given value.

```python
import expecting

assert 10 == expecting.number.le(10)
```

### `expecting.number.gt`

Asserts number is greater than (>) given value.

```python
import expecting

assert 10 == expecting.number.gt(9)
```

### `expecting.number.lt`

Asserts number is lesser than (<) given value.

```python
import expecting

assert 10 == expecting.number.lt(11)
```

### `expecting.number.eq`

Asserts number is equals to given value.

```python
import expecting

assert 10 == expecting.number.eq(10)
```

### `expecting.number.ne`

Asserts number is not equals to given value.

```python
import expecting

assert 10 == expecting.number.ne(9)
```

## `expecting.string`
### `expecting.string.datetime`
### `expecting.string.datetime.iso8601_full`

Asserts string is a valid ISO8601 full format, considering the timezone Z or UTC offset versions.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f+000000.000000') == expecting.string.datetime.iso8601_full()
assert datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ') == expecting.string.datetime.iso8601_full()
```

### `expecting.string.datetime.iso8601_millisecond`

Asserts string is a valid ISO8601 format up to the milliseconds.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') == expecting.string.datetime.iso8601_millisecond()
```

### `expecting.string.datetime.iso8601_second`

Asserts string is a valid ISO8601 format up to the seconds

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%dT%H:%M:%S') == expecting.string.datetime.iso8601_second()
```

### `expecting.string.datetime.iso8601_minute`

Asserts string is a valid ISO8601 format up to the minutes.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%dT%H:%M') == expecting.string.datetime.iso8601_minute()
```

### `expecting.string.datetime.iso8601_hour`

Asserts string is a valid ISO8601 format up to the hours.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%dT%H') == expecting.string.datetime.iso8601_hour()
```

### `expecting.string.datetime.iso8601_day`

Asserts string is a valid ISO8601 format up to the day.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m-%d') == expecting.string.datetime.iso8601_day()
```

### `expecting.string.datetime.iso8601_month`

Asserts string is a valid ISO8601 format up to the month.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y-%m') == expecting.string.datetime.iso8601_month()
```

### `expecting.string.datetime.iso8601_year`

Asserts string is a valid ISO8601 format up to the Year.

```python
from datetime import datetime
import expecting

assert datetime.now().strftime('%Y') == expecting.string.datetime.iso8601_year()
```

### `expecting.string.url`
### `expecting.string.url.with_scheme`

Assert that a string is a valid URL with the given scheme.

```python
import expecting

assert 'https://example.com' == expecting.string.url.with_scheme('https')
```

### `expecting.string.url.with_netloc`

Assert that a string is a valid URL with the given netloc (host and optionally port).

```python
import expecting

assert 'https://example.com:8080' == expecting.string.url.with_netloc('example.com:8080')
assert 'https://example.com' == expecting.string.url.with_netloc('example.com')
assert 'http://example.com' == expecting.string.url.with_netloc('example.com')
```

### `expecting.string.url.with_path`

Assert that a string is a valid URL with the given path.

```python
import expecting

assert 'https://example.com/' == expecting.string.url.with_path('/')
assert 'https://example.com' == expecting.string.url.with_path('')
assert 'https://example.com/some/subfolder' == expecting.string.url.with_path('/some/subfolder')
```


### `expecting.string.url.with_query`

Assert that a string is a valid URL with the given query string.

```python
import expecting

assert 'http://example.com?key=value' == expecting.string.url.with_query('key=value')
assert 'http://example.com?key=value&other' == expecting.string.url.with_query('key=value&other')
assert 'http://example.com?' == expecting.string.url.with_query('')
assert 'http://example.com' == expecting.string.url.with_query('')
```


### `expecting.string.url.with_fragment`

Assert that a string is a valid URL with the given fragment.

```python
import expecting

assert 'https://example.com/path#anchor' == expecting.string.url.with_fragment('anchor')
assert 'https://example.com/path#' == expecting.string.url.with_fragment('')
assert 'https://example.com/path' == expecting.string.url.with_fragment('')
assert 'https://example.com' == expecting.string.url.with_fragment('')
```


### `expecting.string.url.with_components`

Assert that a string is a valid URL with the given components.

```python
import expecting

assert 'https://example.com/path?query=1#anchor' == expecting.string.url.with_components(
    scheme='https',
    netloc='example.com',
    path='/path',
    query='query=1',
    fragment='anchor',
)
```


### `expecting.string.url.any`

Assert that a string is a valid URL.

```python
import expecting

assert 'https://example.com/path?query=1#anchor' == expecting.string.url.any()
assert 'ws://127.0.0.1/ws/' == expecting.string.url.any()
```

### `expecting.string.uuid`
### `expecting.string.uuid.v1`

Asserts that a string is a valid UUID v1 hex

```python
import uuid
import expecting

assert str(uuid.uuid1()) == expecting.string.uuid.v1()
```

### `expecting.string.uuid.v3`

Asserts that a string is a valid UUID v3 hex

```python
import uuid
import expecting

assert str(uuid.uuid3(uuid.uuid1(), 'bogus')) == expecting.string.uuid.v3()
```

### `expecting.string.uuid.v4`

Asserts that a string is a valid UUID v4 hex

```python
import uuid
import expecting

assert str(uuid.uuid4()) == expecting.string.uuid.v4()
```

### `expecting.string.uuid.v5`

Asserts that a string is a valid UUID v5 hex

```python
import uuid
import expecting

assert str(uuid.uuid5(uuid.uuid1(), 'bogus')) == expecting.string.uuid.v5()
```

### `expecting.string.uuid.hex`

Asserts that a string is a valid UUID hex, disregarding the version.

```python
import uuid
import expecting

assert str(uuid.uuid1()) == expecting.string.uuid.hex()
assert str(uuid.uuid3(uuid.uuid1(), 'bogus')) == expecting.string.uuid.hex()
assert str(uuid.uuid4()) == expecting.string.uuid.hex()
assert str(uuid.uuid5(uuid.uuid1(), 'bogus')) == expecting.string.uuid.hex()
```
