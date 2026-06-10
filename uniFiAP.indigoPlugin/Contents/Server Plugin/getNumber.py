#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by Karl Wachs

_NUMBER_CHARS = set("-1234567890.")
_DIGITS = set("1234567890")

_ONE_VALUES = {
	"TRUE", "T", "ON", "HOME", "YES", "JA", "SI", "IGEN", "OUI", "UP", "OPEN", "CLEAR"
}
_ZERO_VALUES = {
	"FALSE", "F", "OFF", "AWAY", "NO", "NON", "NEIN", "NEM", "DOWN", "CLOSED",
	"FAULTED", "FAULT", "EXPIRED"
}
_NEGATIVE_PREFIXES = ("LEAV", "UNK", "LEFT")
_POSITIVE_PREFIXES = ("ENABL", "ARRIV")


def getNumber(val):
	"""Get Number.

	Inputs:
	    val: Caller-supplied value used by this method.
	Outputs:
	    Returns a value to the caller.
	"""
	# test if a val contains a valid number, if not return "x"
	# return the number if any meaningful number (with letters before and after return that number)
	# "a-123.5e" returns -123.5
	# -1.3e5 returns -130000.0
	# -1.3e-5 returns -0.000013
	# "1.3e-5" returns -0.000013
	# "1.3e-5x" returns "x" ( - sign not first position  ..need to include)
	# True, "truE" "on" "ON".. returns 1.0;  False "faLse" "off" returns 0.0
	# "1 2 3" returns "x"
	# "1.2.3" returns "x"
	# "12-5" returns "x"
	try:
		return float(val)
	except (TypeError, ValueError):
		if type(val) is bool:
			return 1.0 if val else 0.0

	if val == "":
		return "x"

	try:
		valText = str(val)
	except Exception:
		return "x"

	firstNumberIndex = -1
	lastNumberIndex = -1
	numberParts = []
	dotCount = 0
	minusCount = 0
	digitCount = 0

	for index, char in enumerate(valText):
		if char not in _NUMBER_CHARS:
			continue
		if firstNumberIndex == -1:
			firstNumberIndex = index
		lastNumberIndex = index
		numberParts.append(char)
		if char == ".":
			dotCount += 1
		elif char == "-":
			minusCount += 1
		elif char in _DIGITS:
			digitCount += 1

	lenNumber = len(numberParts)
	if lenNumber:
		if dotCount > 1:
			return "x"
		if minusCount > 1:
			return "x"
		if digitCount == 0:
			return "x"
		if lenNumber == 1:
			return float(numberParts[0])

		numberText = "".join(numberParts)
		if numberText.find("-") > 0:
			return "x"
		if lastNumberIndex - firstNumberIndex + 1 != lenNumber:
			return "x"
		return float(numberText)

	valText = valText.upper()
	if valText in _ONE_VALUES:
		return 1.0
	if valText in _ZERO_VALUES:
		return 0.0

	if valText.startswith(_NEGATIVE_PREFIXES):
		return -1.0
	if valText.startswith(_POSITIVE_PREFIXES):
		return 1.0
	if valText.startswith("STOP"):
		return 0.0

	return "x"
