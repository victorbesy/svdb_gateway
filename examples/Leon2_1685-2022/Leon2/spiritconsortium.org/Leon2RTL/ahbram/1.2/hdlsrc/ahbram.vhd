-- ****************************************************************************
-- ** Description: ahbram.vhd
-- ** Author:      The SPIRIT Consortium
-- ** Revision:    $Revision: 1506 $
-- ** Date:        $Date: 2009-04-25 23:51:56 -0700 (Sat, 25 Apr 2009) $
-- **
-- ** Copyright (c) 2008, 2009 The SPIRIT Consortium.
-- **
-- ** This work forms part of a deliverable of The SPIRIT Consortium.
-- **
-- ** Use of these materials are governed by the legal terms and conditions
-- ** outlined in the disclaimer available from www.spiritconsortium.org.
-- **
-- ** This source file is provided on an AS IS basis.  The SPIRIT
-- ** Consortium disclaims any warranty express or implied including
-- ** any warranty of merchantability and fitness for use for a
-- ** particular purpose.
-- **
-- ** The user of the source file shall indemnify and hold The SPIRIT
-- ** Consortium and its members harmless from any damages or liability.
-- ** Users are requested to provide feedback to The SPIRIT Consortium
-- ** using either mailto:feedback@lists.spiritconsortium.org or the forms at
-- ** http://www.spiritconsortium.org/about/contact_us/
-- **
-- ** This file may be copied, and distributed, with or without
-- ** modifications; this notice must be included on any copy.
-- ****************************************************************************
-- Derived from code described below
----------------------------------------------------------------------------
--  This file is a part of the LEON VHDL model
--  Copyright (C) 2003 Gaisler Research
--
--  This library is free software; you can redistribute it and/or
--  modify it under the terms of the GNU Lesser General Public
--  License as published by the Free Software Foundation; either
--  version 2 of the License, or (at your option) any later version.
--
--  See the file COPYING.LGPL for the full details of the license.


-----------------------------------------------------------------------------
-- Entity: 	ahbram
-- File:	ahbram.vhd
-- Author:	Jiri Gaisler - Gaisler Reserch
-- Description:	AHB ram. 0-waitstate read, 0/1-waitstate write.
------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_unsigned.conv_integer;
use work.target.all;
use work.config.all;
use work.iface.all;
use work.amba.all;
use work.tech_generic.all;

entity ahbram is
  generic ( abits : integer := 10);
  port (
    rst    : in  std_logic;
    clk    : in  clk_type;
    ahbsi  : in  ahb_slv_in_type;
    ahbso  : out ahb_slv_out_type
  );
end;

architecture rtl of ahbram is

-- synopsys translate_off
    for all: generic_syncram
      use entity work.generic_syncram(behavioral);
-- synopsys translate_on

type reg_type is record
  hwrite : std_logic;
  hready : std_logic;
  hsel   : std_logic;
  addr   : std_logic_vector(abits+1 downto 0);
  size   : std_logic_vector(1 downto 0);
end record;
signal r, c : reg_type;
signal ramsel : std_logic;
signal write : std_logic_vector(3 downto 0);
signal ramaddr  : std_logic_vector(abits-1 downto 0);
begin

  comb : process (ahbsi, r, rst)
  variable bs : std_logic_vector(3 downto 0);
  variable v : reg_type;
  variable haddr  : std_logic_vector(abits-1 downto 0);
  begin
    v := r; v.hready := '1'; bs := (others => '0');
    if (r.hwrite or not r.hready) = '1' then haddr := r.addr(abits+1 downto 2);
    else
      haddr := ahbsi.haddr(abits+1 downto 2); bs := (others => '0'); 
    end if;
    if ahbsi.hready = '1' then 
      v.hsel := ahbsi.hsel and ahbsi.htrans(1);
      v.hwrite := ahbsi.hwrite and v.hsel;
      v.addr := ahbsi.haddr(abits+1 downto 0); 
      v.size := ahbsi.hsize(1 downto 0);
    end if;
    if r.hwrite = '1' then
      case r.size(1 downto 0) is
      when "00" => bs (conv_integer(r.addr(1 downto 0))) := '1';
      when "01" => bs := r.addr(1) & r.addr(1) & not (r.addr(1) & r.addr(1));
      when others => bs := (others => '1');
      end case;
      v.hready := not (v.hsel and not ahbsi.hwrite);
      v.hwrite := v.hwrite and v.hready;
    end if;
    if rst = '0' then v.hwrite := '0'; end if;
    write <= bs; ramsel <= v.hsel or r.hwrite; ahbso.hready <= r.hready; 
    ramaddr <= haddr; c <= v;
  end process;

  ahbso.hresp <= "00"; ahbso.hsplit <= (others => '0');

--  ra : for i in 0 to 3 generate
--    aram : entity  syncram(behav) generic map (abits, 8) port map (
--	ramaddr, clk, ahbsi.hwdata(i*8+7 downto i*8),
--	ahbso.hrdata(i*8+7 downto i*8), ramsel, write(3-i)); 
--  end generate;
    aram0 :  generic_syncram generic map (abits, 8) port map (
	ramaddr, clk, ahbsi.hwdata(7 downto 0),
	ahbso.hrdata(7 downto 0), ramsel, write(3)); 
    aram1 :  generic_syncram generic map (abits, 8) port map (
	ramaddr, clk, ahbsi.hwdata(15 downto 8),
	ahbso.hrdata(15 downto 8), ramsel, write(2)); 
    aram2 :  generic_syncram generic map (abits, 8) port map (
	ramaddr, clk, ahbsi.hwdata(23 downto 16),
	ahbso.hrdata(23 downto 16), ramsel, write(1)); 
    aram3 :  generic_syncram generic map (abits, 8) port map (
	ramaddr, clk, ahbsi.hwdata(31 downto 24),
	ahbso.hrdata(31 downto 24), ramsel, write(0)); 

  reg : process (clk)
  begin
    if rising_edge(clk ) then r <= c; end if;
  end process;
end;
