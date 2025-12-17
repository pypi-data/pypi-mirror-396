"""Helpers for procman"""
import sys, os, time, glob
import subprocess

Verbose = 0

def printTime(): return time.strftime("%m%d:%H%M%S")
def printi(msg): print(f'inf_@{printTime()}: {msg}')
def printw(msg): print(f'WRN_@{printTime()}: {msg}')
def printe(msg): print(f'ERR_{printTime()}: {msg}')
def _printv(msg, level):
    if Verbose >= level:
        print(f'dbg{level}: {msg}')
def printv(msg): _printv(msg, 1)
def printvv(msg): _printv(msg, 2)

