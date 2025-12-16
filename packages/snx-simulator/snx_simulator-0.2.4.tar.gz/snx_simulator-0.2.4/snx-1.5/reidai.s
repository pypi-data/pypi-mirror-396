	lda	$3,	64($0)
	lda	$1,	3($0)
	bal	$2,	foo
	st	$1,	0($0)
	hlt
foo:
	lda	$3,	-2($3)
	st	$2,	0($3)
	st	$1,	1($3)
	bz	$1,	L000
	lda	$1,	-1($1)
	bal	$2,	foo
	ld	$2,	1($3)
	add	$1,	$1,	$2
L000:
	ld	$2,	0($3)
	lda	$3,	2($3)
	bal	$0,	0($2)
