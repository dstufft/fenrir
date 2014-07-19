
#line 1 "fenrir/c/http11/src/http11/http11_parser.rl"
/**
 *
 * Copyright (c) 2010, Zed A. Shaw and Mongrel2 Project Contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *
 *     * Neither the name of the Mongrel2 Project, Zed A. Shaw, nor the names
 *       of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written
 *       permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "http11_parser.h"
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define LEN(AT, FPC) (FPC - buffer - parser->AT)
#define MARK(M,FPC) (parser->M = (FPC) - buffer)
#define PTR_TO(F) (buffer + parser->F)

/** Machine **/


#line 230 "fenrir/c/http11/src/http11/http11_parser.rl"


/** Data **/

#line 57 "fenrir/c/http11/src/http11/http11_parser.c"
static const int http_parser_start = 1;
static const int http_parser_first_final = 197;
static const int http_parser_error = 0;

static const int http_parser_en_main = 1;


#line 234 "fenrir/c/http11/src/http11/http11_parser.rl"

int http_parser_init(http_parser *parser) {
  int cs = 0;

#line 70 "fenrir/c/http11/src/http11/http11_parser.c"
	{
	cs = http_parser_start;
	}

#line 238 "fenrir/c/http11/src/http11/http11_parser.rl"
  parser->cs = cs;
  parser->body_start = 0;
  parser->content_len = 0;
  parser->mark = 0;
  parser->nread = 0;
  parser->field_len = 0;
  parser->field_start = 0;

  return(1);
}


/** exec **/
size_t http_parser_execute(http_parser *parser, const char *buffer, size_t len, size_t off)
{
  const char *p, *pe;
  int cs;

  if(len == 0) return 0;

  cs = parser->cs;

  assert(off <= len && "offset past end of buffer");

  p = buffer+off;
  pe = buffer+len;

  assert(pe - p == (int)len - (int)off && "pointers aren't same distance");


#line 106 "fenrir/c/http11/src/http11/http11_parser.c"
	{
	if ( p == pe )
		goto _test_eof;
	switch ( cs )
	{
case 1:
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto tr0;
	} else if ( (*p) >= 48 )
		goto tr0;
	goto st0;
st0:
cs = 0;
	goto _out;
tr0:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st2;
st2:
	if ( ++p == pe )
		goto _test_eof2;
case 2:
#line 130 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st178;
	} else if ( (*p) >= 48 )
		goto st178;
	goto st0;
tr2:
#line 68 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_method != NULL)
      parser->request_method(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st3;
st3:
	if ( ++p == pe )
		goto _test_eof3;
case 3:
#line 150 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr4;
		case 33: goto tr5;
		case 35: goto tr6;
		case 37: goto tr7;
		case 47: goto tr8;
		case 59: goto tr5;
		case 61: goto tr5;
		case 63: goto tr9;
		case 64: goto tr5;
		case 95: goto tr5;
		case 126: goto tr5;
	}
	if ( (*p) < 65 ) {
		if ( 36 <= (*p) && (*p) <= 57 )
			goto tr5;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto tr10;
	} else
		goto tr10;
	goto st0;
tr4:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
tr39:
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
tr45:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
#line 78 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->fragment != NULL)
      parser->fragment(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
tr48:
#line 78 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->fragment != NULL)
      parser->fragment(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
tr55:
#line 83 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(query_start, p); }
#line 84 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->query_string != NULL)
      parser->query_string(parser->data, PTR_TO(query_start), LEN(query_start, p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
tr59:
#line 84 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->query_string != NULL)
      parser->query_string(parser->data, PTR_TO(query_start), LEN(query_start, p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st4;
st4:
	if ( ++p == pe )
		goto _test_eof4;
case 4:
#line 245 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) == 72 )
		goto tr11;
	goto st0;
tr11:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st5;
st5:
	if ( ++p == pe )
		goto _test_eof5;
case 5:
#line 257 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) == 84 )
		goto st6;
	goto st0;
st6:
	if ( ++p == pe )
		goto _test_eof6;
case 6:
	if ( (*p) == 84 )
		goto st7;
	goto st0;
st7:
	if ( ++p == pe )
		goto _test_eof7;
case 7:
	if ( (*p) == 80 )
		goto st8;
	goto st0;
st8:
	if ( ++p == pe )
		goto _test_eof8;
case 8:
	if ( (*p) == 47 )
		goto st9;
	goto st0;
st9:
	if ( ++p == pe )
		goto _test_eof9;
case 9:
	if ( (*p) == 49 )
		goto st10;
	goto st0;
st10:
	if ( ++p == pe )
		goto _test_eof10;
case 10:
	if ( (*p) == 46 )
		goto st11;
	goto st0;
st11:
	if ( ++p == pe )
		goto _test_eof11;
case 11:
	if ( 48 <= (*p) && (*p) <= 49 )
		goto st12;
	goto st0;
st12:
	if ( ++p == pe )
		goto _test_eof12;
case 12:
	switch( (*p) ) {
		case 10: goto tr19;
		case 13: goto tr20;
	}
	goto st0;
tr19:
#line 89 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_version != NULL)
      parser->http_version(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st13;
tr31:
#line 62 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_field != NULL) {
      parser->http_field(parser->data, PTR_TO(field_start), parser->field_len, PTR_TO(mark), LEN(mark, p));
    }
  }
	goto st13;
st13:
	if ( ++p == pe )
		goto _test_eof13;
case 13:
#line 331 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 10: goto tr22;
		case 13: goto tr23;
		case 33: goto tr21;
		case 124: goto tr21;
		case 126: goto tr21;
	}
	if ( (*p) < 42 ) {
		if ( (*p) < 11 ) {
			if ( 1 <= (*p) && (*p) <= 8 )
				goto tr21;
		} else if ( (*p) > 31 ) {
			if ( 35 <= (*p) && (*p) <= 39 )
				goto tr21;
		} else
			goto tr21;
	} else if ( (*p) > 43 ) {
		if ( (*p) < 48 ) {
			if ( 45 <= (*p) && (*p) <= 46 )
				goto tr21;
		} else if ( (*p) > 57 ) {
			if ( (*p) > 90 ) {
				if ( 94 <= (*p) && (*p) <= 122 )
					goto tr21;
			} else if ( (*p) >= 65 )
				goto tr21;
		} else
			goto tr21;
	} else
		goto tr21;
	goto st0;
tr21:
#line 55 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(field_start, p); }
	goto st14;
st14:
	if ( ++p == pe )
		goto _test_eof14;
case 14:
#line 371 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 33: goto st14;
		case 58: goto tr25;
		case 124: goto st14;
		case 126: goto st14;
	}
	if ( (*p) < 42 ) {
		if ( (*p) < 10 ) {
			if ( 1 <= (*p) && (*p) <= 8 )
				goto st14;
		} else if ( (*p) > 31 ) {
			if ( 35 <= (*p) && (*p) <= 39 )
				goto st14;
		} else
			goto st14;
	} else if ( (*p) > 43 ) {
		if ( (*p) < 48 ) {
			if ( 45 <= (*p) && (*p) <= 46 )
				goto st14;
		} else if ( (*p) > 57 ) {
			if ( (*p) > 90 ) {
				if ( 94 <= (*p) && (*p) <= 122 )
					goto st14;
			} else if ( (*p) >= 65 )
				goto st14;
		} else
			goto st14;
	} else
		goto st14;
	goto st0;
tr25:
#line 56 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    parser->field_len = LEN(field_start, p);
  }
	goto st15;
tr27:
#line 60 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(mark, p); }
	goto st15;
st15:
	if ( ++p == pe )
		goto _test_eof15;
case 15:
#line 416 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 0: goto st0;
		case 9: goto tr27;
		case 10: goto tr28;
		case 32: goto tr27;
		case 127: goto st0;
	}
	goto tr26;
tr26:
#line 60 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(mark, p); }
	goto st16;
st16:
	if ( ++p == pe )
		goto _test_eof16;
case 16:
#line 433 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 0: goto st0;
		case 9: goto tr30;
		case 10: goto tr31;
		case 13: goto tr32;
		case 32: goto tr30;
		case 127: goto st0;
	}
	goto st16;
tr30:
#line 62 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_field != NULL) {
      parser->http_field(parser->data, PTR_TO(field_start), parser->field_len, PTR_TO(mark), LEN(mark, p));
    }
  }
	goto st17;
st17:
	if ( ++p == pe )
		goto _test_eof17;
case 17:
#line 455 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 0: goto st0;
		case 9: goto st17;
		case 10: goto st13;
		case 13: goto st18;
		case 32: goto st17;
		case 127: goto st0;
	}
	goto st16;
tr20:
#line 89 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_version != NULL)
      parser->http_version(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st18;
tr32:
#line 62 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_field != NULL) {
      parser->http_field(parser->data, PTR_TO(field_start), parser->field_len, PTR_TO(mark), LEN(mark, p));
    }
  }
	goto st18;
st18:
	if ( ++p == pe )
		goto _test_eof18;
case 18:
#line 484 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) == 10 )
		goto st13;
	goto st0;
tr28:
#line 60 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(mark, p); }
	goto st19;
st19:
	if ( ++p == pe )
		goto _test_eof19;
case 19:
#line 496 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 0: goto st0;
		case 9: goto tr36;
		case 10: goto tr31;
		case 13: goto tr32;
		case 32: goto tr36;
		case 127: goto st0;
	}
	goto st16;
tr37:
#line 60 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(mark, p); }
	goto st20;
tr36:
#line 62 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->http_field != NULL) {
      parser->http_field(parser->data, PTR_TO(field_start), parser->field_len, PTR_TO(mark), LEN(mark, p));
    }
  }
	goto st20;
st20:
	if ( ++p == pe )
		goto _test_eof20;
case 20:
#line 522 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 0: goto st0;
		case 9: goto tr37;
		case 10: goto st13;
		case 13: goto st18;
		case 32: goto tr37;
		case 127: goto st0;
	}
	goto tr26;
tr22:
#line 55 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(field_start, p); }
#line 99 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    parser->body_start = p - buffer + 1;

    if(parser->header_done != NULL) {
      parser->header_done(parser->data, p + 1, pe - p - 1);
    }
    {p++; cs = 197; goto _out;}
  }
	goto st197;
tr38:
#line 99 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    parser->body_start = p - buffer + 1;

    if(parser->header_done != NULL) {
      parser->header_done(parser->data, p + 1, pe - p - 1);
    }
    {p++; cs = 197; goto _out;}
  }
	goto st197;
st197:
	if ( ++p == pe )
		goto _test_eof197;
case 197:
#line 560 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 33: goto st14;
		case 58: goto tr25;
		case 124: goto st14;
		case 126: goto st14;
	}
	if ( (*p) < 42 ) {
		if ( (*p) < 10 ) {
			if ( 1 <= (*p) && (*p) <= 8 )
				goto st14;
		} else if ( (*p) > 31 ) {
			if ( 35 <= (*p) && (*p) <= 39 )
				goto st14;
		} else
			goto st14;
	} else if ( (*p) > 43 ) {
		if ( (*p) < 48 ) {
			if ( 45 <= (*p) && (*p) <= 46 )
				goto st14;
		} else if ( (*p) > 57 ) {
			if ( (*p) > 90 ) {
				if ( 94 <= (*p) && (*p) <= 122 )
					goto st14;
			} else if ( (*p) >= 65 )
				goto st14;
		} else
			goto st14;
	} else
		goto st14;
	goto st0;
tr23:
#line 55 "fenrir/c/http11/src/http11/http11_parser.rl"
	{ MARK(field_start, p); }
	goto st21;
st21:
	if ( ++p == pe )
		goto _test_eof21;
case 21:
#line 599 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 10: goto tr38;
		case 33: goto st14;
		case 58: goto tr25;
		case 124: goto st14;
		case 126: goto st14;
	}
	if ( (*p) < 42 ) {
		if ( (*p) < 11 ) {
			if ( 1 <= (*p) && (*p) <= 8 )
				goto st14;
		} else if ( (*p) > 31 ) {
			if ( 35 <= (*p) && (*p) <= 39 )
				goto st14;
		} else
			goto st14;
	} else if ( (*p) > 43 ) {
		if ( (*p) < 48 ) {
			if ( 45 <= (*p) && (*p) <= 46 )
				goto st14;
		} else if ( (*p) > 57 ) {
			if ( (*p) > 90 ) {
				if ( 94 <= (*p) && (*p) <= 122 )
					goto st14;
			} else if ( (*p) >= 65 )
				goto st14;
		} else
			goto st14;
	} else
		goto st14;
	goto st0;
tr5:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st22;
st22:
	if ( ++p == pe )
		goto _test_eof22;
case 22:
#line 639 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st22;
		case 35: goto tr41;
		case 37: goto st27;
		case 47: goto st29;
		case 59: goto st22;
		case 61: goto st22;
		case 63: goto tr44;
		case 95: goto st22;
		case 126: goto st22;
	}
	if ( (*p) < 64 ) {
		if ( 36 <= (*p) && (*p) <= 57 )
			goto st22;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st22;
	} else
		goto st22;
	goto st0;
tr6:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st23;
tr41:
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st23;
tr57:
#line 83 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(query_start, p); }
#line 84 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->query_string != NULL)
      parser->query_string(parser->data, PTR_TO(query_start), LEN(query_start, p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st23;
tr61:
#line 84 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->query_string != NULL)
      parser->query_string(parser->data, PTR_TO(query_start), LEN(query_start, p));
  }
#line 73 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_uri != NULL)
      parser->request_uri(parser->data, PTR_TO(mark), LEN(mark, p));
  }
	goto st23;
st23:
	if ( ++p == pe )
		goto _test_eof23;
case 23:
#line 717 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr45;
		case 33: goto tr46;
		case 37: goto tr47;
		case 61: goto tr46;
		case 95: goto tr46;
		case 126: goto tr46;
	}
	if ( (*p) < 63 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto tr46;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto tr46;
	} else
		goto tr46;
	goto st0;
tr46:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st24;
st24:
	if ( ++p == pe )
		goto _test_eof24;
case 24:
#line 743 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr48;
		case 33: goto st24;
		case 37: goto st25;
		case 61: goto st24;
		case 95: goto st24;
		case 126: goto st24;
	}
	if ( (*p) < 63 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st24;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st24;
	} else
		goto st24;
	goto st0;
tr47:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st25;
st25:
	if ( ++p == pe )
		goto _test_eof25;
case 25:
#line 769 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st26;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st26;
	} else
		goto st26;
	goto st0;
st26:
	if ( ++p == pe )
		goto _test_eof26;
case 26:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st24;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st24;
	} else
		goto st24;
	goto st0;
tr7:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st27;
st27:
	if ( ++p == pe )
		goto _test_eof27;
case 27:
#line 800 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st28;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st28;
	} else
		goto st28;
	goto st0;
st28:
	if ( ++p == pe )
		goto _test_eof28;
case 28:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st22;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st22;
	} else
		goto st22;
	goto st0;
tr205:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st29;
st29:
	if ( ++p == pe )
		goto _test_eof29;
case 29:
#line 831 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st29;
		case 35: goto tr41;
		case 37: goto st30;
		case 61: goto st29;
		case 63: goto tr44;
		case 95: goto st29;
		case 126: goto st29;
	}
	if ( (*p) < 64 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st29;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st29;
	} else
		goto st29;
	goto st0;
tr206:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st30;
st30:
	if ( ++p == pe )
		goto _test_eof30;
case 30:
#line 859 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st31;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st31;
	} else
		goto st31;
	goto st0;
st31:
	if ( ++p == pe )
		goto _test_eof31;
case 31:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st29;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st29;
	} else
		goto st29;
	goto st0;
tr9:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
	goto st32;
tr44:
#line 94 "fenrir/c/http11/src/http11/http11_parser.rl"
	{
    if(parser->request_path != NULL)
      parser->request_path(parser->data, PTR_TO(mark), LEN(mark,p));
  }
	goto st32;
st32:
	if ( ++p == pe )
		goto _test_eof32;
case 32:
#line 902 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr55;
		case 33: goto tr56;
		case 35: goto tr57;
		case 37: goto tr58;
		case 61: goto tr56;
		case 95: goto tr56;
		case 126: goto tr56;
	}
	if ( (*p) < 63 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto tr56;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto tr56;
	} else
		goto tr56;
	goto st0;
tr56:
#line 83 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(query_start, p); }
	goto st33;
st33:
	if ( ++p == pe )
		goto _test_eof33;
case 33:
#line 929 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr59;
		case 33: goto st33;
		case 35: goto tr61;
		case 37: goto st34;
		case 61: goto st33;
		case 95: goto st33;
		case 126: goto st33;
	}
	if ( (*p) < 63 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st33;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st33;
	} else
		goto st33;
	goto st0;
tr58:
#line 83 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(query_start, p); }
	goto st34;
st34:
	if ( ++p == pe )
		goto _test_eof34;
case 34:
#line 956 "fenrir/c/http11/src/http11/http11_parser.c"
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st35;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st35;
	} else
		goto st35;
	goto st0;
st35:
	if ( ++p == pe )
		goto _test_eof35;
case 35:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st33;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st33;
	} else
		goto st33;
	goto st0;
tr8:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st36;
st36:
	if ( ++p == pe )
		goto _test_eof36;
case 36:
#line 987 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st29;
		case 35: goto tr41;
		case 37: goto st30;
		case 47: goto st37;
		case 61: goto st29;
		case 63: goto tr44;
		case 95: goto st29;
		case 126: goto st29;
	}
	if ( (*p) < 64 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st29;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st29;
	} else
		goto st29;
	goto st0;
st37:
	if ( ++p == pe )
		goto _test_eof37;
case 37:
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st38;
		case 35: goto tr41;
		case 37: goto st39;
		case 47: goto st29;
		case 58: goto st41;
		case 61: goto st38;
		case 63: goto tr44;
		case 64: goto st45;
		case 91: goto st50;
		case 95: goto st38;
		case 126: goto st38;
	}
	if ( (*p) < 65 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st38;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st38;
	} else
		goto st38;
	goto st0;
st38:
	if ( ++p == pe )
		goto _test_eof38;
case 38:
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st38;
		case 35: goto tr41;
		case 37: goto st39;
		case 47: goto st29;
		case 58: goto st41;
		case 61: goto st38;
		case 63: goto tr44;
		case 64: goto st45;
		case 95: goto st38;
		case 126: goto st38;
	}
	if ( (*p) < 65 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st38;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st38;
	} else
		goto st38;
	goto st0;
st39:
	if ( ++p == pe )
		goto _test_eof39;
case 39:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st40;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st40;
	} else
		goto st40;
	goto st0;
st40:
	if ( ++p == pe )
		goto _test_eof40;
case 40:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st38;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st38;
	} else
		goto st38;
	goto st0;
st41:
	if ( ++p == pe )
		goto _test_eof41;
case 41:
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st42;
		case 35: goto tr41;
		case 37: goto st43;
		case 47: goto st29;
		case 61: goto st42;
		case 63: goto tr44;
		case 64: goto st45;
		case 95: goto st42;
		case 126: goto st42;
	}
	if ( (*p) < 58 ) {
		if ( (*p) > 46 ) {
			if ( 48 <= (*p) && (*p) <= 57 )
				goto st41;
		} else if ( (*p) >= 36 )
			goto st42;
	} else if ( (*p) > 59 ) {
		if ( (*p) > 90 ) {
			if ( 97 <= (*p) && (*p) <= 122 )
				goto st42;
		} else if ( (*p) >= 65 )
			goto st42;
	} else
		goto st42;
	goto st0;
st42:
	if ( ++p == pe )
		goto _test_eof42;
case 42:
	switch( (*p) ) {
		case 33: goto st42;
		case 37: goto st43;
		case 61: goto st42;
		case 64: goto st45;
		case 95: goto st42;
		case 126: goto st42;
	}
	if ( (*p) < 48 ) {
		if ( 36 <= (*p) && (*p) <= 46 )
			goto st42;
	} else if ( (*p) > 59 ) {
		if ( (*p) > 90 ) {
			if ( 97 <= (*p) && (*p) <= 122 )
				goto st42;
		} else if ( (*p) >= 65 )
			goto st42;
	} else
		goto st42;
	goto st0;
st43:
	if ( ++p == pe )
		goto _test_eof43;
case 43:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st44;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st44;
	} else
		goto st44;
	goto st0;
st44:
	if ( ++p == pe )
		goto _test_eof44;
case 44:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st42;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st42;
	} else
		goto st42;
	goto st0;
st45:
	if ( ++p == pe )
		goto _test_eof45;
case 45:
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st46;
		case 35: goto tr41;
		case 37: goto st47;
		case 47: goto st29;
		case 58: goto st49;
		case 61: goto st46;
		case 63: goto tr44;
		case 91: goto st50;
		case 95: goto st46;
		case 126: goto st46;
	}
	if ( (*p) < 65 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st46;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st46;
	} else
		goto st46;
	goto st0;
st46:
	if ( ++p == pe )
		goto _test_eof46;
case 46:
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st46;
		case 35: goto tr41;
		case 37: goto st47;
		case 47: goto st29;
		case 58: goto st49;
		case 61: goto st46;
		case 63: goto tr44;
		case 95: goto st46;
		case 126: goto st46;
	}
	if ( (*p) < 65 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto st46;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto st46;
	} else
		goto st46;
	goto st0;
st47:
	if ( ++p == pe )
		goto _test_eof47;
case 47:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st48;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st48;
	} else
		goto st48;
	goto st0;
st48:
	if ( ++p == pe )
		goto _test_eof48;
case 48:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st46;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st46;
	} else
		goto st46;
	goto st0;
st49:
	if ( ++p == pe )
		goto _test_eof49;
case 49:
	switch( (*p) ) {
		case 32: goto tr39;
		case 35: goto tr41;
		case 47: goto st29;
		case 63: goto tr44;
	}
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st49;
	goto st0;
st50:
	if ( ++p == pe )
		goto _test_eof50;
case 50:
	switch( (*p) ) {
		case 6: goto st51;
		case 58: goto st170;
		case 118: goto st172;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st94;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st94;
	} else
		goto st94;
	goto st0;
st51:
	if ( ++p == pe )
		goto _test_eof51;
case 51:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st52;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st52;
	} else
		goto st52;
	goto st0;
st52:
	if ( ++p == pe )
		goto _test_eof52;
case 52:
	if ( (*p) == 58 )
		goto st56;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st53;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st53;
	} else
		goto st53;
	goto st0;
st53:
	if ( ++p == pe )
		goto _test_eof53;
case 53:
	if ( (*p) == 58 )
		goto st56;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st54;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st54;
	} else
		goto st54;
	goto st0;
st54:
	if ( ++p == pe )
		goto _test_eof54;
case 54:
	if ( (*p) == 58 )
		goto st56;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st55;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st55;
	} else
		goto st55;
	goto st0;
st55:
	if ( ++p == pe )
		goto _test_eof55;
case 55:
	if ( (*p) == 58 )
		goto st56;
	goto st0;
st56:
	if ( ++p == pe )
		goto _test_eof56;
case 56:
	switch( (*p) ) {
		case 49: goto st87;
		case 50: goto st90;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st57;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st93;
	} else
		goto st93;
	goto st0;
st57:
	if ( ++p == pe )
		goto _test_eof57;
case 57:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st80;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st80;
	} else
		goto st80;
	goto st0;
st58:
	if ( ++p == pe )
		goto _test_eof58;
case 58:
	switch( (*p) ) {
		case 49: goto st75;
		case 50: goto st77;
	}
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st59;
	goto st0;
st59:
	if ( ++p == pe )
		goto _test_eof59;
case 59:
	if ( (*p) == 46 )
		goto st60;
	goto st0;
st60:
	if ( ++p == pe )
		goto _test_eof60;
case 60:
	switch( (*p) ) {
		case 49: goto st70;
		case 50: goto st72;
	}
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st61;
	goto st0;
st61:
	if ( ++p == pe )
		goto _test_eof61;
case 61:
	if ( (*p) == 46 )
		goto st62;
	goto st0;
st62:
	if ( ++p == pe )
		goto _test_eof62;
case 62:
	switch( (*p) ) {
		case 49: goto st65;
		case 50: goto st67;
	}
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st63;
	goto st0;
st63:
	if ( ++p == pe )
		goto _test_eof63;
case 63:
	if ( (*p) == 93 )
		goto st64;
	goto st0;
st64:
	if ( ++p == pe )
		goto _test_eof64;
case 64:
	switch( (*p) ) {
		case 32: goto tr39;
		case 35: goto tr41;
		case 47: goto st29;
		case 58: goto st49;
		case 63: goto tr44;
	}
	goto st0;
st65:
	if ( ++p == pe )
		goto _test_eof65;
case 65:
	if ( (*p) == 93 )
		goto st64;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st66;
	goto st0;
st66:
	if ( ++p == pe )
		goto _test_eof66;
case 66:
	if ( (*p) == 93 )
		goto st64;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st63;
	goto st0;
st67:
	if ( ++p == pe )
		goto _test_eof67;
case 67:
	switch( (*p) ) {
		case 48: goto st68;
		case 53: goto st69;
		case 93: goto st64;
	}
	goto st0;
st68:
	if ( ++p == pe )
		goto _test_eof68;
case 68:
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st63;
	goto st0;
st69:
	if ( ++p == pe )
		goto _test_eof69;
case 69:
	if ( (*p) == 48 )
		goto st63;
	goto st0;
st70:
	if ( ++p == pe )
		goto _test_eof70;
case 70:
	if ( (*p) == 46 )
		goto st62;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st71;
	goto st0;
st71:
	if ( ++p == pe )
		goto _test_eof71;
case 71:
	if ( (*p) == 46 )
		goto st62;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st61;
	goto st0;
st72:
	if ( ++p == pe )
		goto _test_eof72;
case 72:
	switch( (*p) ) {
		case 46: goto st62;
		case 48: goto st73;
		case 53: goto st74;
	}
	goto st0;
st73:
	if ( ++p == pe )
		goto _test_eof73;
case 73:
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st61;
	goto st0;
st74:
	if ( ++p == pe )
		goto _test_eof74;
case 74:
	if ( (*p) == 48 )
		goto st61;
	goto st0;
st75:
	if ( ++p == pe )
		goto _test_eof75;
case 75:
	if ( (*p) == 46 )
		goto st60;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st76;
	goto st0;
st76:
	if ( ++p == pe )
		goto _test_eof76;
case 76:
	if ( (*p) == 46 )
		goto st60;
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st59;
	goto st0;
st77:
	if ( ++p == pe )
		goto _test_eof77;
case 77:
	switch( (*p) ) {
		case 46: goto st60;
		case 48: goto st78;
		case 53: goto st79;
	}
	goto st0;
st78:
	if ( ++p == pe )
		goto _test_eof78;
case 78:
	if ( 48 <= (*p) && (*p) <= 57 )
		goto st59;
	goto st0;
st79:
	if ( ++p == pe )
		goto _test_eof79;
case 79:
	if ( (*p) == 48 )
		goto st59;
	goto st0;
st80:
	if ( ++p == pe )
		goto _test_eof80;
case 80:
	if ( (*p) == 58 )
		goto st83;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st81;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st81;
	} else
		goto st81;
	goto st0;
st81:
	if ( ++p == pe )
		goto _test_eof81;
case 81:
	if ( (*p) == 58 )
		goto st83;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st82;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st82;
	} else
		goto st82;
	goto st0;
st82:
	if ( ++p == pe )
		goto _test_eof82;
case 82:
	if ( (*p) == 58 )
		goto st83;
	goto st0;
st83:
	if ( ++p == pe )
		goto _test_eof83;
case 83:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st84;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st84;
	} else
		goto st84;
	goto st0;
st84:
	if ( ++p == pe )
		goto _test_eof84;
case 84:
	if ( (*p) == 93 )
		goto st64;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st85;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st85;
	} else
		goto st85;
	goto st0;
st85:
	if ( ++p == pe )
		goto _test_eof85;
case 85:
	if ( (*p) == 93 )
		goto st64;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st86;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st86;
	} else
		goto st86;
	goto st0;
st86:
	if ( ++p == pe )
		goto _test_eof86;
case 86:
	if ( (*p) == 93 )
		goto st64;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st63;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st63;
	} else
		goto st63;
	goto st0;
st87:
	if ( ++p == pe )
		goto _test_eof87;
case 87:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st88;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st80;
	} else
		goto st80;
	goto st0;
st88:
	if ( ++p == pe )
		goto _test_eof88;
case 88:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st89;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st81;
	} else
		goto st81;
	goto st0;
st89:
	if ( ++p == pe )
		goto _test_eof89;
case 89:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st82;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st82;
	} else
		goto st82;
	goto st0;
st90:
	if ( ++p == pe )
		goto _test_eof90;
case 90:
	switch( (*p) ) {
		case 46: goto st58;
		case 48: goto st91;
		case 53: goto st92;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st80;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st80;
	} else
		goto st80;
	goto st0;
st91:
	if ( ++p == pe )
		goto _test_eof91;
case 91:
	if ( (*p) == 58 )
		goto st83;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st89;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st81;
	} else
		goto st81;
	goto st0;
st92:
	if ( ++p == pe )
		goto _test_eof92;
case 92:
	switch( (*p) ) {
		case 48: goto st89;
		case 58: goto st83;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st81;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st81;
	} else
		goto st81;
	goto st0;
st93:
	if ( ++p == pe )
		goto _test_eof93;
case 93:
	if ( (*p) == 58 )
		goto st83;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st80;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st80;
	} else
		goto st80;
	goto st0;
st94:
	if ( ++p == pe )
		goto _test_eof94;
case 94:
	if ( (*p) == 58 )
		goto st98;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st95;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st95;
	} else
		goto st95;
	goto st0;
st95:
	if ( ++p == pe )
		goto _test_eof95;
case 95:
	if ( (*p) == 58 )
		goto st98;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st96;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st96;
	} else
		goto st96;
	goto st0;
st96:
	if ( ++p == pe )
		goto _test_eof96;
case 96:
	if ( (*p) == 58 )
		goto st98;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st97;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st97;
	} else
		goto st97;
	goto st0;
st97:
	if ( ++p == pe )
		goto _test_eof97;
case 97:
	if ( (*p) == 58 )
		goto st98;
	goto st0;
st98:
	if ( ++p == pe )
		goto _test_eof98;
case 98:
	if ( (*p) == 58 )
		goto st169;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st99;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st99;
	} else
		goto st99;
	goto st0;
st99:
	if ( ++p == pe )
		goto _test_eof99;
case 99:
	if ( (*p) == 58 )
		goto st103;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st100;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st100;
	} else
		goto st100;
	goto st0;
st100:
	if ( ++p == pe )
		goto _test_eof100;
case 100:
	if ( (*p) == 58 )
		goto st103;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st101;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st101;
	} else
		goto st101;
	goto st0;
st101:
	if ( ++p == pe )
		goto _test_eof101;
case 101:
	if ( (*p) == 58 )
		goto st103;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st102;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st102;
	} else
		goto st102;
	goto st0;
st102:
	if ( ++p == pe )
		goto _test_eof102;
case 102:
	if ( (*p) == 58 )
		goto st103;
	goto st0;
st103:
	if ( ++p == pe )
		goto _test_eof103;
case 103:
	if ( (*p) == 58 )
		goto st168;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st104;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st104;
	} else
		goto st104;
	goto st0;
st104:
	if ( ++p == pe )
		goto _test_eof104;
case 104:
	if ( (*p) == 58 )
		goto st108;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st105;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st105;
	} else
		goto st105;
	goto st0;
st105:
	if ( ++p == pe )
		goto _test_eof105;
case 105:
	if ( (*p) == 58 )
		goto st108;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st106;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st106;
	} else
		goto st106;
	goto st0;
st106:
	if ( ++p == pe )
		goto _test_eof106;
case 106:
	if ( (*p) == 58 )
		goto st108;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st107;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st107;
	} else
		goto st107;
	goto st0;
st107:
	if ( ++p == pe )
		goto _test_eof107;
case 107:
	if ( (*p) == 58 )
		goto st108;
	goto st0;
st108:
	if ( ++p == pe )
		goto _test_eof108;
case 108:
	if ( (*p) == 58 )
		goto st167;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st109;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st109;
	} else
		goto st109;
	goto st0;
st109:
	if ( ++p == pe )
		goto _test_eof109;
case 109:
	if ( (*p) == 58 )
		goto st113;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st110;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st110;
	} else
		goto st110;
	goto st0;
st110:
	if ( ++p == pe )
		goto _test_eof110;
case 110:
	if ( (*p) == 58 )
		goto st113;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st111;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st111;
	} else
		goto st111;
	goto st0;
st111:
	if ( ++p == pe )
		goto _test_eof111;
case 111:
	if ( (*p) == 58 )
		goto st113;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st112;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st112;
	} else
		goto st112;
	goto st0;
st112:
	if ( ++p == pe )
		goto _test_eof112;
case 112:
	if ( (*p) == 58 )
		goto st113;
	goto st0;
st113:
	if ( ++p == pe )
		goto _test_eof113;
case 113:
	if ( (*p) == 58 )
		goto st166;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st114;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st114;
	} else
		goto st114;
	goto st0;
st114:
	if ( ++p == pe )
		goto _test_eof114;
case 114:
	if ( (*p) == 58 )
		goto st118;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st115;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st115;
	} else
		goto st115;
	goto st0;
st115:
	if ( ++p == pe )
		goto _test_eof115;
case 115:
	if ( (*p) == 58 )
		goto st118;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st116;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st116;
	} else
		goto st116;
	goto st0;
st116:
	if ( ++p == pe )
		goto _test_eof116;
case 116:
	if ( (*p) == 58 )
		goto st118;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st117;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st117;
	} else
		goto st117;
	goto st0;
st117:
	if ( ++p == pe )
		goto _test_eof117;
case 117:
	if ( (*p) == 58 )
		goto st118;
	goto st0;
st118:
	if ( ++p == pe )
		goto _test_eof118;
case 118:
	if ( (*p) == 58 )
		goto st154;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st119;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st119;
	} else
		goto st119;
	goto st0;
st119:
	if ( ++p == pe )
		goto _test_eof119;
case 119:
	if ( (*p) == 58 )
		goto st123;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st120;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st120;
	} else
		goto st120;
	goto st0;
st120:
	if ( ++p == pe )
		goto _test_eof120;
case 120:
	if ( (*p) == 58 )
		goto st123;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st121;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st121;
	} else
		goto st121;
	goto st0;
st121:
	if ( ++p == pe )
		goto _test_eof121;
case 121:
	if ( (*p) == 58 )
		goto st123;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st122;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st122;
	} else
		goto st122;
	goto st0;
st122:
	if ( ++p == pe )
		goto _test_eof122;
case 122:
	if ( (*p) == 58 )
		goto st123;
	goto st0;
st123:
	if ( ++p == pe )
		goto _test_eof123;
case 123:
	if ( (*p) == 58 )
		goto st153;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st124;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st124;
	} else
		goto st124;
	goto st0;
st124:
	if ( ++p == pe )
		goto _test_eof124;
case 124:
	if ( (*p) == 58 )
		goto st128;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st125;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st125;
	} else
		goto st125;
	goto st0;
st125:
	if ( ++p == pe )
		goto _test_eof125;
case 125:
	if ( (*p) == 58 )
		goto st128;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st126;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st126;
	} else
		goto st126;
	goto st0;
st126:
	if ( ++p == pe )
		goto _test_eof126;
case 126:
	if ( (*p) == 58 )
		goto st128;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st127;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st127;
	} else
		goto st127;
	goto st0;
st127:
	if ( ++p == pe )
		goto _test_eof127;
case 127:
	if ( (*p) == 58 )
		goto st128;
	goto st0;
st128:
	if ( ++p == pe )
		goto _test_eof128;
case 128:
	if ( (*p) == 58 )
		goto st129;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st124;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st124;
	} else
		goto st124;
	goto st0;
st129:
	if ( ++p == pe )
		goto _test_eof129;
case 129:
	switch( (*p) ) {
		case 49: goto st146;
		case 50: goto st149;
		case 93: goto st64;
	}
	if ( (*p) < 48 ) {
		if ( 2 <= (*p) && (*p) <= 3 )
			goto st51;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 70 ) {
			if ( 97 <= (*p) && (*p) <= 102 )
				goto st152;
		} else if ( (*p) >= 65 )
			goto st152;
	} else
		goto st130;
	goto st0;
st130:
	if ( ++p == pe )
		goto _test_eof130;
case 130:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st131;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st131;
	} else
		goto st131;
	goto st0;
st131:
	if ( ++p == pe )
		goto _test_eof131;
case 131:
	switch( (*p) ) {
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st132;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st132;
	} else
		goto st132;
	goto st0;
st132:
	if ( ++p == pe )
		goto _test_eof132;
case 132:
	switch( (*p) ) {
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st133;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st133;
	} else
		goto st133;
	goto st0;
st133:
	if ( ++p == pe )
		goto _test_eof133;
case 133:
	switch( (*p) ) {
		case 58: goto st134;
		case 93: goto st64;
	}
	goto st0;
st134:
	if ( ++p == pe )
		goto _test_eof134;
case 134:
	switch( (*p) ) {
		case 49: goto st139;
		case 50: goto st142;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st135;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st145;
	} else
		goto st145;
	goto st0;
st135:
	if ( ++p == pe )
		goto _test_eof135;
case 135:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st136;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st136;
	} else
		goto st136;
	goto st0;
st136:
	if ( ++p == pe )
		goto _test_eof136;
case 136:
	switch( (*p) ) {
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st137;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st137;
	} else
		goto st137;
	goto st0;
st137:
	if ( ++p == pe )
		goto _test_eof137;
case 137:
	switch( (*p) ) {
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st138;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st138;
	} else
		goto st138;
	goto st0;
st138:
	if ( ++p == pe )
		goto _test_eof138;
case 138:
	switch( (*p) ) {
		case 58: goto st83;
		case 93: goto st64;
	}
	goto st0;
st139:
	if ( ++p == pe )
		goto _test_eof139;
case 139:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st140;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st136;
	} else
		goto st136;
	goto st0;
st140:
	if ( ++p == pe )
		goto _test_eof140;
case 140:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st141;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st137;
	} else
		goto st137;
	goto st0;
st141:
	if ( ++p == pe )
		goto _test_eof141;
case 141:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st138;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st138;
	} else
		goto st138;
	goto st0;
st142:
	if ( ++p == pe )
		goto _test_eof142;
case 142:
	switch( (*p) ) {
		case 46: goto st58;
		case 48: goto st143;
		case 53: goto st144;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st136;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st136;
	} else
		goto st136;
	goto st0;
st143:
	if ( ++p == pe )
		goto _test_eof143;
case 143:
	switch( (*p) ) {
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st141;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st137;
	} else
		goto st137;
	goto st0;
st144:
	if ( ++p == pe )
		goto _test_eof144;
case 144:
	switch( (*p) ) {
		case 48: goto st141;
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st137;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st137;
	} else
		goto st137;
	goto st0;
st145:
	if ( ++p == pe )
		goto _test_eof145;
case 145:
	switch( (*p) ) {
		case 58: goto st83;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st136;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st136;
	} else
		goto st136;
	goto st0;
st146:
	if ( ++p == pe )
		goto _test_eof146;
case 146:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st147;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st131;
	} else
		goto st131;
	goto st0;
st147:
	if ( ++p == pe )
		goto _test_eof147;
case 147:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st148;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st132;
	} else
		goto st132;
	goto st0;
st148:
	if ( ++p == pe )
		goto _test_eof148;
case 148:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st133;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st133;
	} else
		goto st133;
	goto st0;
st149:
	if ( ++p == pe )
		goto _test_eof149;
case 149:
	switch( (*p) ) {
		case 46: goto st58;
		case 48: goto st150;
		case 53: goto st151;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st131;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st131;
	} else
		goto st131;
	goto st0;
st150:
	if ( ++p == pe )
		goto _test_eof150;
case 150:
	switch( (*p) ) {
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st148;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st132;
	} else
		goto st132;
	goto st0;
st151:
	if ( ++p == pe )
		goto _test_eof151;
case 151:
	switch( (*p) ) {
		case 48: goto st148;
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st132;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st132;
	} else
		goto st132;
	goto st0;
st152:
	if ( ++p == pe )
		goto _test_eof152;
case 152:
	switch( (*p) ) {
		case 58: goto st134;
		case 93: goto st64;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st131;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st131;
	} else
		goto st131;
	goto st0;
st153:
	if ( ++p == pe )
		goto _test_eof153;
case 153:
	switch( (*p) ) {
		case 49: goto st146;
		case 50: goto st149;
	}
	if ( (*p) < 48 ) {
		if ( 2 <= (*p) && (*p) <= 3 )
			goto st51;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 70 ) {
			if ( 97 <= (*p) && (*p) <= 102 )
				goto st152;
		} else if ( (*p) >= 65 )
			goto st152;
	} else
		goto st130;
	goto st0;
st154:
	if ( ++p == pe )
		goto _test_eof154;
case 154:
	switch( (*p) ) {
		case 49: goto st159;
		case 50: goto st162;
	}
	if ( (*p) < 48 ) {
		if ( 2 <= (*p) && (*p) <= 3 )
			goto st51;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 70 ) {
			if ( 97 <= (*p) && (*p) <= 102 )
				goto st165;
		} else if ( (*p) >= 65 )
			goto st165;
	} else
		goto st155;
	goto st0;
st155:
	if ( ++p == pe )
		goto _test_eof155;
case 155:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st156;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st156;
	} else
		goto st156;
	goto st0;
st156:
	if ( ++p == pe )
		goto _test_eof156;
case 156:
	if ( (*p) == 58 )
		goto st134;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st157;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st157;
	} else
		goto st157;
	goto st0;
st157:
	if ( ++p == pe )
		goto _test_eof157;
case 157:
	if ( (*p) == 58 )
		goto st134;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st158;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st158;
	} else
		goto st158;
	goto st0;
st158:
	if ( ++p == pe )
		goto _test_eof158;
case 158:
	if ( (*p) == 58 )
		goto st134;
	goto st0;
st159:
	if ( ++p == pe )
		goto _test_eof159;
case 159:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st160;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st156;
	} else
		goto st156;
	goto st0;
st160:
	if ( ++p == pe )
		goto _test_eof160;
case 160:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st161;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st157;
	} else
		goto st157;
	goto st0;
st161:
	if ( ++p == pe )
		goto _test_eof161;
case 161:
	switch( (*p) ) {
		case 46: goto st58;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st158;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st158;
	} else
		goto st158;
	goto st0;
st162:
	if ( ++p == pe )
		goto _test_eof162;
case 162:
	switch( (*p) ) {
		case 46: goto st58;
		case 48: goto st163;
		case 53: goto st164;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st156;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st156;
	} else
		goto st156;
	goto st0;
st163:
	if ( ++p == pe )
		goto _test_eof163;
case 163:
	if ( (*p) == 58 )
		goto st134;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st161;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st157;
	} else
		goto st157;
	goto st0;
st164:
	if ( ++p == pe )
		goto _test_eof164;
case 164:
	switch( (*p) ) {
		case 48: goto st161;
		case 58: goto st134;
	}
	if ( (*p) < 65 ) {
		if ( 49 <= (*p) && (*p) <= 57 )
			goto st157;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st157;
	} else
		goto st157;
	goto st0;
st165:
	if ( ++p == pe )
		goto _test_eof165;
case 165:
	if ( (*p) == 58 )
		goto st134;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st156;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st156;
	} else
		goto st156;
	goto st0;
st166:
	if ( ++p == pe )
		goto _test_eof166;
case 166:
	if ( (*p) < 48 ) {
		if ( 2 <= (*p) && (*p) <= 3 )
			goto st51;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 70 ) {
			if ( 97 <= (*p) && (*p) <= 102 )
				goto st52;
		} else if ( (*p) >= 65 )
			goto st52;
	} else
		goto st52;
	goto st0;
st167:
	if ( ++p == pe )
		goto _test_eof167;
case 167:
	if ( 2 <= (*p) && (*p) <= 3 )
		goto st51;
	goto st0;
st168:
	if ( ++p == pe )
		goto _test_eof168;
case 168:
	if ( (*p) == 3 )
		goto st51;
	goto st0;
st169:
	if ( ++p == pe )
		goto _test_eof169;
case 169:
	if ( (*p) == 4 )
		goto st51;
	goto st0;
st170:
	if ( ++p == pe )
		goto _test_eof170;
case 170:
	if ( (*p) == 58 )
		goto st171;
	goto st0;
st171:
	if ( ++p == pe )
		goto _test_eof171;
case 171:
	switch( (*p) ) {
		case 49: goto st146;
		case 50: goto st149;
		case 93: goto st64;
	}
	if ( (*p) < 48 ) {
		if ( 2 <= (*p) && (*p) <= 5 )
			goto st51;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 70 ) {
			if ( 97 <= (*p) && (*p) <= 102 )
				goto st152;
		} else if ( (*p) >= 65 )
			goto st152;
	} else
		goto st130;
	goto st0;
st172:
	if ( ++p == pe )
		goto _test_eof172;
case 172:
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st173;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st173;
	} else
		goto st173;
	goto st0;
st173:
	if ( ++p == pe )
		goto _test_eof173;
case 173:
	if ( (*p) == 46 )
		goto st174;
	if ( (*p) < 65 ) {
		if ( 48 <= (*p) && (*p) <= 57 )
			goto st173;
	} else if ( (*p) > 70 ) {
		if ( 97 <= (*p) && (*p) <= 102 )
			goto st173;
	} else
		goto st173;
	goto st0;
st174:
	if ( ++p == pe )
		goto _test_eof174;
case 174:
	switch( (*p) ) {
		case 33: goto st175;
		case 36: goto st175;
		case 61: goto st175;
		case 95: goto st175;
		case 126: goto st175;
	}
	if ( (*p) < 48 ) {
		if ( 38 <= (*p) && (*p) <= 46 )
			goto st175;
	} else if ( (*p) > 59 ) {
		if ( (*p) > 90 ) {
			if ( 97 <= (*p) && (*p) <= 122 )
				goto st175;
		} else if ( (*p) >= 65 )
			goto st175;
	} else
		goto st175;
	goto st0;
st175:
	if ( ++p == pe )
		goto _test_eof175;
case 175:
	switch( (*p) ) {
		case 33: goto st175;
		case 36: goto st175;
		case 61: goto st175;
		case 93: goto st64;
		case 95: goto st175;
		case 126: goto st175;
	}
	if ( (*p) < 48 ) {
		if ( 38 <= (*p) && (*p) <= 46 )
			goto st175;
	} else if ( (*p) > 59 ) {
		if ( (*p) > 90 ) {
			if ( 97 <= (*p) && (*p) <= 122 )
				goto st175;
		} else if ( (*p) >= 65 )
			goto st175;
	} else
		goto st175;
	goto st0;
tr10:
#line 52 "fenrir/c/http11/src/http11/http11_parser.rl"
	{MARK(mark, p); }
	goto st176;
st176:
	if ( ++p == pe )
		goto _test_eof176;
case 176:
#line 3019 "fenrir/c/http11/src/http11/http11_parser.c"
	switch( (*p) ) {
		case 32: goto tr39;
		case 33: goto st22;
		case 35: goto tr41;
		case 37: goto st27;
		case 43: goto st176;
		case 47: goto st29;
		case 58: goto st177;
		case 59: goto st22;
		case 61: goto st22;
		case 63: goto tr44;
		case 64: goto st22;
		case 95: goto st22;
		case 126: goto st22;
	}
	if ( (*p) < 45 ) {
		if ( 36 <= (*p) && (*p) <= 44 )
			goto st22;
	} else if ( (*p) > 57 ) {
		if ( (*p) > 90 ) {
			if ( 97 <= (*p) && (*p) <= 122 )
				goto st176;
		} else if ( (*p) >= 65 )
			goto st176;
	} else
		goto st176;
	goto st0;
st177:
	if ( ++p == pe )
		goto _test_eof177;
case 177:
	switch( (*p) ) {
		case 32: goto tr4;
		case 33: goto tr205;
		case 35: goto tr6;
		case 37: goto tr206;
		case 47: goto tr8;
		case 61: goto tr205;
		case 63: goto tr9;
		case 95: goto tr205;
		case 126: goto tr205;
	}
	if ( (*p) < 64 ) {
		if ( 36 <= (*p) && (*p) <= 59 )
			goto tr205;
	} else if ( (*p) > 90 ) {
		if ( 97 <= (*p) && (*p) <= 122 )
			goto tr205;
	} else
		goto tr205;
	goto st0;
st178:
	if ( ++p == pe )
		goto _test_eof178;
case 178:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st179;
	} else if ( (*p) >= 48 )
		goto st179;
	goto st0;
st179:
	if ( ++p == pe )
		goto _test_eof179;
case 179:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st180;
	} else if ( (*p) >= 48 )
		goto st180;
	goto st0;
st180:
	if ( ++p == pe )
		goto _test_eof180;
case 180:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st181;
	} else if ( (*p) >= 48 )
		goto st181;
	goto st0;
st181:
	if ( ++p == pe )
		goto _test_eof181;
case 181:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st182;
	} else if ( (*p) >= 48 )
		goto st182;
	goto st0;
st182:
	if ( ++p == pe )
		goto _test_eof182;
case 182:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st183;
	} else if ( (*p) >= 48 )
		goto st183;
	goto st0;
st183:
	if ( ++p == pe )
		goto _test_eof183;
case 183:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st184;
	} else if ( (*p) >= 48 )
		goto st184;
	goto st0;
st184:
	if ( ++p == pe )
		goto _test_eof184;
case 184:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st185;
	} else if ( (*p) >= 48 )
		goto st185;
	goto st0;
st185:
	if ( ++p == pe )
		goto _test_eof185;
case 185:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st186;
	} else if ( (*p) >= 48 )
		goto st186;
	goto st0;
st186:
	if ( ++p == pe )
		goto _test_eof186;
case 186:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st187;
	} else if ( (*p) >= 48 )
		goto st187;
	goto st0;
st187:
	if ( ++p == pe )
		goto _test_eof187;
case 187:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st188;
	} else if ( (*p) >= 48 )
		goto st188;
	goto st0;
st188:
	if ( ++p == pe )
		goto _test_eof188;
case 188:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st189;
	} else if ( (*p) >= 48 )
		goto st189;
	goto st0;
st189:
	if ( ++p == pe )
		goto _test_eof189;
case 189:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st190;
	} else if ( (*p) >= 48 )
		goto st190;
	goto st0;
st190:
	if ( ++p == pe )
		goto _test_eof190;
case 190:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st191;
	} else if ( (*p) >= 48 )
		goto st191;
	goto st0;
st191:
	if ( ++p == pe )
		goto _test_eof191;
case 191:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st192;
	} else if ( (*p) >= 48 )
		goto st192;
	goto st0;
st192:
	if ( ++p == pe )
		goto _test_eof192;
case 192:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st193;
	} else if ( (*p) >= 48 )
		goto st193;
	goto st0;
st193:
	if ( ++p == pe )
		goto _test_eof193;
case 193:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st194;
	} else if ( (*p) >= 48 )
		goto st194;
	goto st0;
st194:
	if ( ++p == pe )
		goto _test_eof194;
case 194:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st195;
	} else if ( (*p) >= 48 )
		goto st195;
	goto st0;
st195:
	if ( ++p == pe )
		goto _test_eof195;
case 195:
	if ( (*p) == 32 )
		goto tr2;
	if ( (*p) > 57 ) {
		if ( 65 <= (*p) && (*p) <= 90 )
			goto st196;
	} else if ( (*p) >= 48 )
		goto st196;
	goto st0;
st196:
	if ( ++p == pe )
		goto _test_eof196;
case 196:
	if ( (*p) == 32 )
		goto tr2;
	goto st0;
	}
	_test_eof2: cs = 2; goto _test_eof;
	_test_eof3: cs = 3; goto _test_eof;
	_test_eof4: cs = 4; goto _test_eof;
	_test_eof5: cs = 5; goto _test_eof;
	_test_eof6: cs = 6; goto _test_eof;
	_test_eof7: cs = 7; goto _test_eof;
	_test_eof8: cs = 8; goto _test_eof;
	_test_eof9: cs = 9; goto _test_eof;
	_test_eof10: cs = 10; goto _test_eof;
	_test_eof11: cs = 11; goto _test_eof;
	_test_eof12: cs = 12; goto _test_eof;
	_test_eof13: cs = 13; goto _test_eof;
	_test_eof14: cs = 14; goto _test_eof;
	_test_eof15: cs = 15; goto _test_eof;
	_test_eof16: cs = 16; goto _test_eof;
	_test_eof17: cs = 17; goto _test_eof;
	_test_eof18: cs = 18; goto _test_eof;
	_test_eof19: cs = 19; goto _test_eof;
	_test_eof20: cs = 20; goto _test_eof;
	_test_eof197: cs = 197; goto _test_eof;
	_test_eof21: cs = 21; goto _test_eof;
	_test_eof22: cs = 22; goto _test_eof;
	_test_eof23: cs = 23; goto _test_eof;
	_test_eof24: cs = 24; goto _test_eof;
	_test_eof25: cs = 25; goto _test_eof;
	_test_eof26: cs = 26; goto _test_eof;
	_test_eof27: cs = 27; goto _test_eof;
	_test_eof28: cs = 28; goto _test_eof;
	_test_eof29: cs = 29; goto _test_eof;
	_test_eof30: cs = 30; goto _test_eof;
	_test_eof31: cs = 31; goto _test_eof;
	_test_eof32: cs = 32; goto _test_eof;
	_test_eof33: cs = 33; goto _test_eof;
	_test_eof34: cs = 34; goto _test_eof;
	_test_eof35: cs = 35; goto _test_eof;
	_test_eof36: cs = 36; goto _test_eof;
	_test_eof37: cs = 37; goto _test_eof;
	_test_eof38: cs = 38; goto _test_eof;
	_test_eof39: cs = 39; goto _test_eof;
	_test_eof40: cs = 40; goto _test_eof;
	_test_eof41: cs = 41; goto _test_eof;
	_test_eof42: cs = 42; goto _test_eof;
	_test_eof43: cs = 43; goto _test_eof;
	_test_eof44: cs = 44; goto _test_eof;
	_test_eof45: cs = 45; goto _test_eof;
	_test_eof46: cs = 46; goto _test_eof;
	_test_eof47: cs = 47; goto _test_eof;
	_test_eof48: cs = 48; goto _test_eof;
	_test_eof49: cs = 49; goto _test_eof;
	_test_eof50: cs = 50; goto _test_eof;
	_test_eof51: cs = 51; goto _test_eof;
	_test_eof52: cs = 52; goto _test_eof;
	_test_eof53: cs = 53; goto _test_eof;
	_test_eof54: cs = 54; goto _test_eof;
	_test_eof55: cs = 55; goto _test_eof;
	_test_eof56: cs = 56; goto _test_eof;
	_test_eof57: cs = 57; goto _test_eof;
	_test_eof58: cs = 58; goto _test_eof;
	_test_eof59: cs = 59; goto _test_eof;
	_test_eof60: cs = 60; goto _test_eof;
	_test_eof61: cs = 61; goto _test_eof;
	_test_eof62: cs = 62; goto _test_eof;
	_test_eof63: cs = 63; goto _test_eof;
	_test_eof64: cs = 64; goto _test_eof;
	_test_eof65: cs = 65; goto _test_eof;
	_test_eof66: cs = 66; goto _test_eof;
	_test_eof67: cs = 67; goto _test_eof;
	_test_eof68: cs = 68; goto _test_eof;
	_test_eof69: cs = 69; goto _test_eof;
	_test_eof70: cs = 70; goto _test_eof;
	_test_eof71: cs = 71; goto _test_eof;
	_test_eof72: cs = 72; goto _test_eof;
	_test_eof73: cs = 73; goto _test_eof;
	_test_eof74: cs = 74; goto _test_eof;
	_test_eof75: cs = 75; goto _test_eof;
	_test_eof76: cs = 76; goto _test_eof;
	_test_eof77: cs = 77; goto _test_eof;
	_test_eof78: cs = 78; goto _test_eof;
	_test_eof79: cs = 79; goto _test_eof;
	_test_eof80: cs = 80; goto _test_eof;
	_test_eof81: cs = 81; goto _test_eof;
	_test_eof82: cs = 82; goto _test_eof;
	_test_eof83: cs = 83; goto _test_eof;
	_test_eof84: cs = 84; goto _test_eof;
	_test_eof85: cs = 85; goto _test_eof;
	_test_eof86: cs = 86; goto _test_eof;
	_test_eof87: cs = 87; goto _test_eof;
	_test_eof88: cs = 88; goto _test_eof;
	_test_eof89: cs = 89; goto _test_eof;
	_test_eof90: cs = 90; goto _test_eof;
	_test_eof91: cs = 91; goto _test_eof;
	_test_eof92: cs = 92; goto _test_eof;
	_test_eof93: cs = 93; goto _test_eof;
	_test_eof94: cs = 94; goto _test_eof;
	_test_eof95: cs = 95; goto _test_eof;
	_test_eof96: cs = 96; goto _test_eof;
	_test_eof97: cs = 97; goto _test_eof;
	_test_eof98: cs = 98; goto _test_eof;
	_test_eof99: cs = 99; goto _test_eof;
	_test_eof100: cs = 100; goto _test_eof;
	_test_eof101: cs = 101; goto _test_eof;
	_test_eof102: cs = 102; goto _test_eof;
	_test_eof103: cs = 103; goto _test_eof;
	_test_eof104: cs = 104; goto _test_eof;
	_test_eof105: cs = 105; goto _test_eof;
	_test_eof106: cs = 106; goto _test_eof;
	_test_eof107: cs = 107; goto _test_eof;
	_test_eof108: cs = 108; goto _test_eof;
	_test_eof109: cs = 109; goto _test_eof;
	_test_eof110: cs = 110; goto _test_eof;
	_test_eof111: cs = 111; goto _test_eof;
	_test_eof112: cs = 112; goto _test_eof;
	_test_eof113: cs = 113; goto _test_eof;
	_test_eof114: cs = 114; goto _test_eof;
	_test_eof115: cs = 115; goto _test_eof;
	_test_eof116: cs = 116; goto _test_eof;
	_test_eof117: cs = 117; goto _test_eof;
	_test_eof118: cs = 118; goto _test_eof;
	_test_eof119: cs = 119; goto _test_eof;
	_test_eof120: cs = 120; goto _test_eof;
	_test_eof121: cs = 121; goto _test_eof;
	_test_eof122: cs = 122; goto _test_eof;
	_test_eof123: cs = 123; goto _test_eof;
	_test_eof124: cs = 124; goto _test_eof;
	_test_eof125: cs = 125; goto _test_eof;
	_test_eof126: cs = 126; goto _test_eof;
	_test_eof127: cs = 127; goto _test_eof;
	_test_eof128: cs = 128; goto _test_eof;
	_test_eof129: cs = 129; goto _test_eof;
	_test_eof130: cs = 130; goto _test_eof;
	_test_eof131: cs = 131; goto _test_eof;
	_test_eof132: cs = 132; goto _test_eof;
	_test_eof133: cs = 133; goto _test_eof;
	_test_eof134: cs = 134; goto _test_eof;
	_test_eof135: cs = 135; goto _test_eof;
	_test_eof136: cs = 136; goto _test_eof;
	_test_eof137: cs = 137; goto _test_eof;
	_test_eof138: cs = 138; goto _test_eof;
	_test_eof139: cs = 139; goto _test_eof;
	_test_eof140: cs = 140; goto _test_eof;
	_test_eof141: cs = 141; goto _test_eof;
	_test_eof142: cs = 142; goto _test_eof;
	_test_eof143: cs = 143; goto _test_eof;
	_test_eof144: cs = 144; goto _test_eof;
	_test_eof145: cs = 145; goto _test_eof;
	_test_eof146: cs = 146; goto _test_eof;
	_test_eof147: cs = 147; goto _test_eof;
	_test_eof148: cs = 148; goto _test_eof;
	_test_eof149: cs = 149; goto _test_eof;
	_test_eof150: cs = 150; goto _test_eof;
	_test_eof151: cs = 151; goto _test_eof;
	_test_eof152: cs = 152; goto _test_eof;
	_test_eof153: cs = 153; goto _test_eof;
	_test_eof154: cs = 154; goto _test_eof;
	_test_eof155: cs = 155; goto _test_eof;
	_test_eof156: cs = 156; goto _test_eof;
	_test_eof157: cs = 157; goto _test_eof;
	_test_eof158: cs = 158; goto _test_eof;
	_test_eof159: cs = 159; goto _test_eof;
	_test_eof160: cs = 160; goto _test_eof;
	_test_eof161: cs = 161; goto _test_eof;
	_test_eof162: cs = 162; goto _test_eof;
	_test_eof163: cs = 163; goto _test_eof;
	_test_eof164: cs = 164; goto _test_eof;
	_test_eof165: cs = 165; goto _test_eof;
	_test_eof166: cs = 166; goto _test_eof;
	_test_eof167: cs = 167; goto _test_eof;
	_test_eof168: cs = 168; goto _test_eof;
	_test_eof169: cs = 169; goto _test_eof;
	_test_eof170: cs = 170; goto _test_eof;
	_test_eof171: cs = 171; goto _test_eof;
	_test_eof172: cs = 172; goto _test_eof;
	_test_eof173: cs = 173; goto _test_eof;
	_test_eof174: cs = 174; goto _test_eof;
	_test_eof175: cs = 175; goto _test_eof;
	_test_eof176: cs = 176; goto _test_eof;
	_test_eof177: cs = 177; goto _test_eof;
	_test_eof178: cs = 178; goto _test_eof;
	_test_eof179: cs = 179; goto _test_eof;
	_test_eof180: cs = 180; goto _test_eof;
	_test_eof181: cs = 181; goto _test_eof;
	_test_eof182: cs = 182; goto _test_eof;
	_test_eof183: cs = 183; goto _test_eof;
	_test_eof184: cs = 184; goto _test_eof;
	_test_eof185: cs = 185; goto _test_eof;
	_test_eof186: cs = 186; goto _test_eof;
	_test_eof187: cs = 187; goto _test_eof;
	_test_eof188: cs = 188; goto _test_eof;
	_test_eof189: cs = 189; goto _test_eof;
	_test_eof190: cs = 190; goto _test_eof;
	_test_eof191: cs = 191; goto _test_eof;
	_test_eof192: cs = 192; goto _test_eof;
	_test_eof193: cs = 193; goto _test_eof;
	_test_eof194: cs = 194; goto _test_eof;
	_test_eof195: cs = 195; goto _test_eof;
	_test_eof196: cs = 196; goto _test_eof;

	_test_eof: {}
	_out: {}
	}

#line 268 "fenrir/c/http11/src/http11/http11_parser.rl"

  assert(p <= pe && "Buffer overflow after parsing.");

  if (!http_parser_has_error(parser)) {
      parser->cs = cs;
  }

  parser->nread += p - (buffer + off);

  assert(parser->nread <= len && "nread longer than length");
  assert(parser->body_start <= len && "body starts after buffer end");
  assert(parser->mark < len && "mark is after buffer end");
  assert(parser->field_len <= len && "field has length longer than whole buffer");
  assert(parser->field_start < len && "field starts after buffer end");

  return(parser->nread);
}

int http_parser_finish(http_parser *parser)
{
  if (http_parser_has_error(parser) ) {
    return -1;
  } else if (http_parser_is_finished(parser) ) {
    return 1;
  } else {
    return 0;
  }
}

int http_parser_has_error(http_parser *parser) {
  return parser->cs == http_parser_error;
}

int http_parser_is_finished(http_parser *parser) {
  return parser->cs >= http_parser_first_final;
}
