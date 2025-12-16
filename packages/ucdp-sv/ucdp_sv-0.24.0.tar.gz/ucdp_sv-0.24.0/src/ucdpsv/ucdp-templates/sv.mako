##
## MIT License
##
## Copyright (c) 2024 nbiotcloud
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
<%!
import ucdp as u
import ucdpsv as usv
%>

<%inherit file="main.mako"/>


<%block name="main">\
// =============================================================================
//
//   ${" ".join(output_tags)}
//
//   ${makolator.info.genwarning}
//
// =============================================================================
${self.copyright()}\
// =============================================================================
${self.fileheader()}\
// =============================================================================

${self.header()}\

${self.beginmod()}\

${self.logic(indent=2)}\

${self.endmod()}\

${self.footer()}\

// =============================================================================
//
//   ${" ".join(output_tags)}
//
//   ${makolator.info.genwarning}
//
// =============================================================================
</%block>

<%def name="copyright(obj=None)">\
${u.get_copyright(obj or mod) | comment}
</%def>\

<%def name="fileheader()">\
<%
overview = mod.get_overview()
topmodref = u.TopModRef.from_mod(mod)
%>\
//
% if topmodref:
// Update via:  ${u.consts.CLINAME} gen ${str(topmodref.new(sub=None))}
% else:
// Update via:  <parent module>
% endif
//
// Library:     ${mod.libname}
// Module:      ${mod.modname}
// Data Model:  ${mod.__class__.__name__}
//              ${u.modutil.get_file(mod.__class__, basedir=output_filepath.parent).as_posix()}
% if mod.insts:
// Submodules:
%   for modinst in mod.insts:
%     if modinst.virtual:
//              ${modinst.modname} *
%     else:
//              ${modinst.modname} ${modinst.name}
%     endif
%   endfor
% endif
//
% if overview:
//
${overview | comment}
//
% endif
</%def>


<%def name="header()">\
`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden
</%def>


<%def name="beginmod(wirenames=None)">\
<%
rslvr = usv.get_resolver(mod)
params = rslvr.get_paramdecls(mod.namespace, indent=2)
ports = rslvr.get_portdecls(mod.ports, wirenames=wirenames, indent=2)
%>\
module ${mod.modname}\
% if params:
 #(
${params.get()}
)\
% endif
% if ports:
%   if params:
 (
%   else:
 (
%   endif
${ports.get()}
)\
% else:
()\
% endif
;
</%def>


<%def name="params(is_last=False)">\
<%
rslvr = usv.get_resolver(mod)
params = rslvr.get_paramdecls(mod.namespace, is_last=is_last)
%>\
${params.get()}
</%def>


<%def name="ports(is_last=False, wirenames=None, no_comments=False)">\
<%
rslvr = usv.get_resolver(mod)
ports = rslvr.get_portdecls(mod.ports, is_last=is_last, wirenames=wirenames, no_comment=no_comments)
%>\
${ports.get()}
</%def>


<%def name="logic(indent=0, skip=None)">\
<%
skip = u.split(skip)
%>\
% if "localparams" not in skip:
${self.localparams(indent=indent)}\
% endif
% if "signals" not in skip:
${self.signals(indent=indent)}\
% endif
% if "insts" not in skip:
${self.insts(indent=indent)}\
% endif
% if "flipflops" not in skip:
${self.flipflops(indent=indent)}\
% endif
% if "muxes" not in skip:
${self.muxes(indent=indent)}\
% endif
% if "assigns" not in skip:
${self.assigns(indent=indent)}\
% endif
</%def>


<%def name="localparams(indent=0, title='Local Parameter')">\
<%
rslvr = usv.get_resolver(mod)
align = rslvr.get_localparamdecls(mod.namespace, indent=indent)
pre = " " * indent
%>\
% if align:
%   if title:


${pre}// ------------------------------------------------------
${pre}//  ${title}
${pre}// ------------------------------------------------------
%   endif
${align.get()}
% endif
</%def>


<%def name="signals(indent=0, idents=None, title='Signals', wirenames=None)">\
<%
if idents is None:
  idents = mod.portssignals
rslvr = usv.get_resolver(mod)
align = rslvr.get_signaldecls(idents, indent=indent, wirenames=wirenames)
pre = " " * indent
%>\
% if align:
%   if title:


${pre}// ------------------------------------------------------
${pre}//  ${title}
${pre}// ------------------------------------------------------
%   endif
${align.get()}
% endif
</%def>


<%def name="insts(indent=0)">\
% for modinst in mod.insts:
%   if not modinst.virtual:


${inst(modinst, indent)}
%   endif
% endfor
</%def>


<%def name="inst(inst, indent=0)">\
<%
  inst = mod.get_inst(inst)
  pre = " " * indent
  comment = inst.doc.comment or f"{inst.libname}.{inst.modname}: {inst.name}"
  rslvr = usv.get_resolver(mod, inst=inst)
  params = rslvr.get_instparams(inst, indent=indent+2)
  ports = rslvr.get_instcons(mod.get_instcons(inst), indent=indent+2)
%>\
${pre}// ------------------------------------------------------
% for line in comment.split("\n"):
${pre}//  ${line}
% endfor
${pre}// ------------------------------------------------------
${pre}${inst.modname}\
% if params:
 #(
${params.get()}
${pre}) ${inst.name}\
% else:
 ${inst.name}\
% endif
% if ports:
%   if params:
 (
%   else:
 (
%   endif
${ports.get()}
${pre})\
% else:
 ()\
% endif
;\
</%def>


<%def name="instparams(inst, is_last=False, indent=0)">\
<%
  inst = mod.get_inst(inst)
  rslvr = usv.get_resolver(mod)
  align = rslvr.get_instparams(inst, is_last=is_last, indent=indent)
%>\
${align.get()}
</%def>


<%def name="instcons(inst, skips=None, is_last=False, indent=0)">\
<%
  inst = mod.get_inst(mod)
  rslvr = usv.get_resolver(mod)
  align = rslvr.get_instcons(mod.get_instcons(inst), skips=skips, is_last=is_last, indent=indent)
%>\
${align.get()}
</%def>


<%def name="flipflops(indent=0)">\
<%
  rslvr = usv.get_resolver(mod)
  flipflops = mod.flipflops
  pre = " " * indent
%>\
% if flipflops:


${pre}// ------------------------------------------------------
${pre}//  Flip-Flops
${pre}// ------------------------------------------------------
% endif
% for idx, flipflop in enumerate(flipflops):

${pre}always_ff @(posedge ${flipflop.clk.name} or negedge ${flipflop.rst_an.name}) begin: proc_seq_${idx}
${pre}  if (${flipflop.rst_an.name} == 1'b0) begin
${rslvr.get_defaults(flipflop.defaults(), indent=indent+4, oper="<= ").get()}
% if flipflop.rst is not None:
${pre}  end else if (${rslvr.resolve(flipflop.rst)}) begin
${rslvr.get_defaults(flipflop.defaults(), indent=indent+4, oper="<= ").get()}
% endif
% if flipflop.ena is not None:
${pre}  end else if (${rslvr.resolve(flipflop.ena)}) begin
% else:
${pre}  end else begin
% endif
${rslvr.get_assigns(flipflop, indent=indent+4, oper=f"<= {rslvr.ff_dly}").get()}
${pre}  end
${pre}end
% endfor
</%def>


<%def name="muxes(indent=0)">\
% for mux_ in mod.muxes:


${mux(mux_, indent)}\
% endfor
</%def>


<%def name="mux(mux, indent=0)">\
<%
  rslvr = usv.get_resolver(mod)
  mux = mod.get_mux(mux)
  pre = " " * indent
  comment = mux.doc.comment or f"Multiplexer {mux.name}"
%>\
${pre}// ------------------------------------------------------
% for line in comment.split("\n"):
${pre}//  ${line}
% endfor
${pre}// ------------------------------------------------------
% if mux:
${pre}always_comb begin : proc_${mux.name}
${pre}  // defaults
${rslvr.get_assigns(mux.defaults(), indent=indent+2, oper="=").get()}
%   for sel, conds in mux:

${pre}  case (${sel}) inside
<% cases, defaultcase = rslvr.split_mux_conds(sel, conds) %>\
%     for cond, assigns in cases:
${pre}    ${cond}: begin
${rslvr.get_assigns(assigns, indent=indent+6, oper="=").get()}
${pre}    end
%     endfor
%   if defaultcase:
${pre}    default: begin // ${defaultcase[0]}
${rslvr.get_assigns(defaultcase[1], indent=indent+6, oper="=").get()}
${pre}    end
%   endif
${pre}  endcase
%   endfor
${pre}end
% else:
${pre}// empty
% endif
</%def>


<%def name="assigns(indent=0, title='Assigns')">\
<%
  rslvr = usv.get_resolver(mod)
  align = rslvr.get_assigns(mod.assigns, indent=indent)
  pre = " " * indent
%>\
% if align:
%   if title:

${pre}// ------------------------------------------------------
${pre}//  Assigns
${pre}// ------------------------------------------------------
%   endif
${align.get()}
% endif
</%def>


<%def name="endmod()">\
endmodule // ${mod.modname}
</%def>


<%def name="footer()">\
`default_nettype wire
`end_keywords
</%def>


<%def name="head(nologic=False)">\
${self.copyright()}\
// =============================================================================
${self.fileheader()}\
// =============================================================================

${self.header()}\

${self.beginmod()}\

% if not nologic:
${self.logic(indent=2)}\

% endif
</%def>

<%def name="tail()">\
${self.endmod()}\

${self.footer()}\
</%def>


<%def name="create_inplace()">\
// GENERATE INPLACE BEGIN head()
// GENERATE INPLACE END head

// Add your hand-written code here - remove this line afterwards

// GENERATE INPLACE BEGIN tail()
// GENERATE INPLACE END tail
</%def>
