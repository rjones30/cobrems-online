#!/bin/bash
if false; then
	export ROOTSYS=/usr/local/root
	if [[ -n "$LD_LIBRARY_PATH" ]]; then
    	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib
	else
    	export LD_LIBRARY_PATH=$ROOTSYS/lib
	fi
	if [[ -n "$PYTHONPATH" ]]; then
    	export PYTHONPATH=$PYTHONPATH:$ROOTSYS/lib
	else
    	export PYTHONPATH=$ROOTSYS/lib
	fi
fi

exec python `echo $0 | sed 's/.cgi/.py/'`
