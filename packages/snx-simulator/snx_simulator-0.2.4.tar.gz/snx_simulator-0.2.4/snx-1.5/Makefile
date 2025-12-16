SHELL=bash
FPGABOARD=mu200ea40
SYNTHEOPT=-O -neg_res
VCD=+vcd=1
P=
TEST1=if
TEST2=for
TEST3=recur
TEST4=sort
CLEANS=snx$(P) snx$(P).v snx.mem sim.log snxc/snxc.exe snxc/snxi.exe snxasm/snxasm.exe test.v snx.vcd
CLEAN1=$(TEST1).mem $(TEST1).dat $(TEST1).s
CLEAN2=$(TEST2).mem $(TEST2).dat $(TEST2).s
CLEAN3=$(TEST3).mem $(TEST3).dat $(TEST3).s
CLEAN4=$(TEST4).mem $(TEST4).dat $(TEST4).s
CLEANT=$(TARGET).mem $(TARGET).dat $(TARGET).s
CLEAN=$(CLEANS) $(CLEAN1) $(CLEAN2) $(CLEAN3) $(CLEAN4) $(CLEANT) cpu.v
SNXEXE=./snx$(P)
SNXMEM=snx.mem
NSL2VL=nsl2vl
VERILOG=iverilog
VVP=vvp

reidai.mem: reidai.s snxasm/snxasm.exe
	./snxasm/snxasm.exe < reidai.s | tee $@

reidai:	reidai.mem $(SNXEXE)
	cp reidai.mem $(SNXMEM)
	$(VVP) $(SNXEXE) $(VCD)| tee sim.log

sim1:
	make TARGET=$(TEST1) sim

sim2:
	make TARGET=$(TEST2) sim

sim3:
	make TARGET=$(TEST3) sim

sim4:
	make TARGET=$(TEST4) sim

sim:	$(TARGET).mem $(SNXEXE)
	cp $(TARGET).mem $(SNXMEM)
	$(VVP) $(SNXEXE) $(VCD)| tee sim.log


$(TARGET).mem:	$(TARGET).s snxasm/snxasm.exe
	./snxasm/snxasm.exe < $(TARGET).s | tee $(TARGET).mem

$(TARGET).dat:	$(TARGET).s snxasm/snxasm.exe
	./snxasm/snxasm.exe b < $(TARGET).s > $(TARGET).dat

$(TARGET).hex:	$(TARGET).s snxasm/snxasm.exe
	./snxasm/snxasm.exe i < $(TARGET).s > $(TARGET).hex

$(TARGET).s:	snxc/snxc.exe snxasm/snxasm.exe $(TARGET).sc
	./snxc/snxc.exe < $(TARGET).sc | tee $(TARGET).s

compile:
	make $(TARGET).s

inter:	snxc/snxi
	./snxc/snxi < $(TARGET).sc

snxc/snxc.exe:
	( cd snxc; make CC=gcc snxc)

snxc/snxi.exe:
	( cd snxc; make CC=gcc snxi)

snxasm/snxasm.exe:
	( cd snxasm; make CC=gcc snxasm)

$(SNXEXE): snx$(P).v main$(P).v
	$(VERILOG) -o $(SNXEXE) snx$(P).v main$(P).v

snx$(P).v:	snx$(P).nsl
	$(NSL2VL) snx$(P).nsl -sim -neg_res

synthe:	snx.nsl mem.h $(FPGABOARD).nsl
	$(NSL2VL) snx$(P).nsl $(SYNTHEOPT)
	$(NSL2VL) $(FPGABOARD).nsl $(SYNTHEOPT)

distclean:
	make clean
	-rm snxc/snxc.exe
	-rm snxasm/snxasm.exe

clean:
	-rm $(CLEAN) 2> /dev/null
	( cd snxc; make clean ) 2> /dev/null
	( cd snxasm; make clean ) 2> /dev/null

