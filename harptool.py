#!/usr/bin/python
#
# harptool.py - cgi script for running the Hall D coherent bremsstrahlung
#               harp scan fitter, a ROOT tool written by R.T.Jones.
#
# author: richard.t.jones at uconn.edu
# version: november 9, 2018

import sys
sys.path.insert(0, "/usr/local/root/lib/root")

import numpy
import ROOT
ROOT.gROOT.IsBatch()

import os
import cgi
import html
import cgitb
cgitb.enable()

slimits = (100, 200)
sigma_spec = (0.5, 0.5)

def print_head():
   print("Content-Type: text/html")
   print()
   print("<html>")
   print("<head>")
   print("<title>Hall D Electron Beam Harp Scan Fitting Tool</title>")
   print("</head>")
   print("<body>")
   print("<form action=\"harptool.cgi\" method=\"get\" enctype=\"application/x-www-form-urlencoded\">")
   print("<table>")
   print("<tr><td colspan=\"5\" height=\"150\">")
   print("<h2 align=\"center\">Hall D Electron Beam Harp Scan Fitting Tool</h2>")
   print("<p align=\"center\">Richard Jones, University of Connecticut <br />")
   print("November 9, 2018</p>")
   print("</td></tr>")

def print_tail():
   print("</table>")
   print("</form>")
   print("</body>")
   print("</html>")

def set_parameter(par, desc, default, unit):
   if par in form:
      value = html.escape(form.getfirst(par))
   else:
      value = default
   if str("default " + par) in form:
      value = default
   print("<td>" + desc + ": </td><td>",)
   print("<input type=\"text\" name=\"" + par + "\" value=\"" + str(value) + "\" size=\"6\" />",)
   print(unit)
   print("<input type=\"submit\" name=\"default " + par + "\" value=\"default\"></td>")

def fit_model(var, par):
   """
   var[0] = s coordinate (m)
   par[0] = s coordinate (m) of focus
   par[1] = sigma at the focus (mm)
   par[2] = emittance (mm.mrad)
   """
   return (par[1]**2 + (par[2]/par[1] * (var[0] - par[0]))**2)**0.5

def fit_model_gradient(var, par):
   """
   var[0] = s coordinate (m)
   par[0] = s coordinate (m) of focus
   par[1] = sigma at the focus (mm)
   par[2] = emittance (mm.mrad)
   """
   y = (par[1]**2 + (par[2]/par[1] * (var[0] - par[0]))**2)**0.5
   dyds0 = -(par[2]/par[1])**2 * (var[0] - par[0]) / y
   dydsig0 = (par[1]**2 - (par[2]/par[1] * (var[0] - par[0]))**2) / (y * par[1])
   return (dyds0, dydsig0)

def fit_and_plot(sx, sigx, sigxerr, sy, sigy, sigyerr):
   zero = [0] * len(sx)
   xfitf = ROOT.TF1("xfitf", fit_model, slimits[0], slimits[1], 3)
   xfitf.SetParameter(0, slimits[1])
   xfitf.SetParameter(1, 1.0)
   xfitf.FixParameter(2, float(html.escape(form.getfirst("emittance_x"))))
   xfitf.SetLineColor(ROOT.kRed)
   xdata = ROOT.TGraphErrors(len(sx), numpy.array(sx, dtype=float),
                                      numpy.array(sigx, dtype=float),
                                      numpy.array(zero, dtype=float),
                                      numpy.array(sigxerr, dtype=float))
   xfit = xdata.Fit(xfitf, "qs")
   xdata.SetLineColor(ROOT.kRed)
   xdata.SetLineWidth(2)
   xdata.SetMarkerColor(ROOT.kRed)
   xdata.SetMarkerStyle(20)

   ss = []
   x0 = []
   x1 = []
   par = [xfit.Parameter(0), xfit.Parameter(1), xfit.Parameter(2)]
   covar = xfit.GetCovarianceMatrix()
   minvar = 0.01**2
   for n in range(0, 101):
      s = slimits[0] + n * (slimits[1] - slimits[0]) / 100
      xmu = fit_model([s], par)
      gra = fit_model_gradient([s], par)
      ss.append(s)
      xsigma = (covar(0,0) * gra[0]**2 + covar(1,1) * gra[1]**2 +
                2 * covar(0,1) * gra[0] * gra[1] + minvar)**0.5
      x0.append(xmu - xsigma)
      x1.append(xmu + xsigma)
      if x0[-1] < 0:
         x0[-1] = 0
   xshade = ROOT.TGraph(2 * len(ss), numpy.array(ss + ss[::-1], dtype=float),
                                     numpy.array(x0 + x1[::-1], dtype=float))
   xshade.SetFillColorAlpha(ROOT.kRed, 0.2);

   yfitf = ROOT.TF1("yfitf", fit_model, slimits[0], slimits[1], 3)
   yfitf.SetParameter(0, slimits[1])
   yfitf.SetParameter(1, 1.0)
   yfitf.FixParameter(2, float(html.escape(form.getfirst("emittance_y"))))
   yfitf.SetLineColor(ROOT.kBlue)
   ydata = ROOT.TGraphErrors(len(sy), numpy.array(sy, dtype=float),
                                      numpy.array(sigy, dtype=float),
                                      numpy.array(zero, dtype=float),
                                      numpy.array(sigyerr, dtype=float))
   yfit = ydata.Fit(yfitf, "qs")
   ydata.SetLineColor(ROOT.kBlue)
   ydata.SetLineWidth(2)
   ydata.SetMarkerColor(ROOT.kBlue)
   ydata.SetMarkerStyle(20)

   ss = []
   y0 = []
   y1 = []
   par = [yfit.Parameter(0), yfit.Parameter(1), yfit.Parameter(2)]
   covar = yfit.GetCovarianceMatrix()
   minvar = 0.01**2
   for n in range(0, 101):
      s = slimits[0] + n * (slimits[1] - slimits[0]) / 100
      ymu = fit_model([s], par)
      gra = fit_model_gradient([s], par)
      ss.append(s)
      ysigma = (covar(0,0) * gra[0]**2 + covar(1,1) * gra[1]**2 +
                2 * covar(0,1) * gra[0] * gra[1] + minvar)**0.5
      y0.append(ymu - ysigma)
      y1.append(ymu + ysigma)
      if y0[-1] < 0:
         y0[-1] = 0
   yshade = ROOT.TGraph(2 * len(ss), numpy.array(ss + ss[::-1], dtype=float),
                                     numpy.array(y0 + y1[::-1], dtype=float))
   yshade.SetFillColorAlpha(ROOT.kBlue, 0.2);

   c1 = ROOT.TCanvas("c1", "", 800, 600)
   xfitf.SetTitle("") # "sigma x vs accelerator s")
   xfitf.GetXaxis().SetTitle("accelerator s coordinate (m)")
   xfitf.GetYaxis().SetTitle("#sigma_{x} (mm)")
   xfitf.SetMinimum(0)
   xfitf.SetMaximum(max(x1))
   xfitf.Draw()
   xdata.Draw("P")
   xshade.Draw("f")
   scol = float(html.escape(form.getfirst("collimator_spos")))
   gcol = ROOT.TGraph(2, numpy.array([scol] * 2, dtype=float), numpy.array([0, 1.5], dtype=float))
   gcol.Draw("L")
   xspec = ROOT.TArrow(scol, sigma_spec[0], slimits[1], sigma_spec[0], 0.03, "<|")
   xspec.SetAngle(35)
   xspec.Draw()
   c1.Update()
   c1.Print(workdir + "harp-x-" + fitimage)
   c1.Print(workdir + "harp-x-" + str(os.getpid()) + ".pdf")
   yfitf.SetTitle("") # "sigma y vs accelerator s")
   yfitf.GetXaxis().SetTitle("accelerator s coordinate (m)")
   yfitf.GetYaxis().SetTitle("#sigma_{y} (mm)")
   yfitf.SetMinimum(0)
   yfitf.SetMaximum(max(y1))
   yfitf.Draw()
   ydata.Draw("P")
   yshade.Draw("f")
   gcol.Draw("L")
   yspec = ROOT.TArrow(scol, sigma_spec[1], slimits[1], sigma_spec[1], 0.03, "<|")
   yspec.SetAngle(35)
   yspec.Draw()
   c1.Update()
   c1.Print(workdir + "harp-y-" + fitimage)
   c1.Print(workdir + "harp-y-" + str(os.getpid()) + ".pdf")
   print("<tr><td colspan=\"5\">")
   print("<div align=\"center\"><img src=\"work/harp-x-" + fitimage + "\"></div>")
   print("<div align=\"center\"><img src=\"work/harp-y-" + fitimage + "\"></div>")
   print("</td></tr>")

# main execution starts here

print_head()

workdir = os.path.dirname(sys.argv[0]) + "/work/"
fitimage = str(os.getpid()) + ".png"

form = cgi.FieldStorage()

print("<tr>")
set_parameter("harp5C11_xsigma", "5C11 harp x sigma", 0, "mm")
print("<td width=\"50\"></td>")
set_parameter("harp5C11_xsigma_err", "5C11 harp x sigma error", 0.030, "mm")
print("</tr>")
print("<tr>")
set_parameter("harp5C11_ysigma", "5C11 harp y sigma", 0, "mm")
print("<td></td>")
set_parameter("harp5C11_ysigma_err", "5C11 harp y sigma error", 0.030, "mm")
print("</tr>")
print("<tr>")
set_parameter("harp5C11B_xsigma", "5C11B harp x sigma", 0, "mm")
print("<td></td>")
set_parameter("harp5C11B_xsigma_err", "5C11B harp x sigma error", 0.050, "mm")
print("</tr>")
print("<tr>")
set_parameter("harp5C11B_ysigma", "5C11B harp y sigma", 0, "mm")
print("<td></td>")
set_parameter("harp5C11B_ysigma_err", "5C11B harp y sigma error", 0.150, "mm")
print("</tr>")
print("<tr>")
set_parameter("radHarp_xsigma", "radiator harp x sigma", 0, "mm")
print("<td></td>")
set_parameter("radHarp_xsigma_err", "radiator harp x sigma error", 0.020, "mm")
print("</tr>")
print("<tr>")
set_parameter("radHarp_ysigma", "radiator harp y sigma", 0, "mm")
print("<td></td>")
set_parameter("radHarp_ysigma_err", "radiator harp y sigma error", 0.020, "mm")
print("</tr>")
print("<tr>")
print("<td colspan=\"2\" bgcolor=\"#dfcfaf\">")
print("<i>Enter measured values in the above input boxes,</i>")
print("</td><td></td>")
set_parameter("harp5C11_spos", "s of 5C11 harps", 102.97, "m")
print("</tr>")
print("<tr>")
print("<td colspan=\"2\" bgcolor=\"#dfcfaf\">")
print("<i>defaults are generally ok for the other fields.</i>")
print("</td><td></td>")
set_parameter("harp5C11B_spos", "s of 5C11B harps", 115.11, "m")
print("</tr>")
print("<tr>")
set_parameter("emittance_x", "x emittance of e-beam", 0.0041, "mm.mrad")
print("<td></td>")
set_parameter("radHarp_spos", "s of radiator harp", 119.70, "m")
print("</tr>")
print("<tr>")
set_parameter("emittance_y", "y emittance of e-beam", 0.00233, "mm.mrad")
print("<td></td>")
set_parameter("collimator_spos", "s of primary collimator", 194.92, "m")
print("</tr>")
print("<tr><td colspan=\"5\" align=\"center\" height=\"80\" valign=\"middle\" >")
print("<input type=\"submit\" name=\"fit\" value=\"fit and plot\" \>")
print("</td></tr>")

sx = []
sy = []
sigx = []
sigy = []
sigxerr = []
sigyerr = []
zero_values = 0
breaking_bad = 0
for key in ("harp5C11", "harp5C11B", "radHarp"):
   try:
      sx.append(float(html.escape(form.getfirst(key + "_spos"))))
      sy.append(float(html.escape(form.getfirst(key + "_spos"))))
      sigx.append(float(html.escape(form.getfirst(key + "_xsigma"))))
      sigxerr.append(float(html.escape(form.getfirst(key + "_xsigma_err"))))
      sigy.append(float(html.escape(form.getfirst(key + "_ysigma"))))
      sigyerr.append(float(html.escape(form.getfirst(key + "_ysigma_err"))))
   except:
      breaking_bad += 1
      continue
   if sigxerr[-1] > 0:
      if sigx[-1] == 0:
         zero_values += 1
   else:
      sx.pop()
      sigx.pop()
      sigxerr.pop()
   if sigyerr[-1] > 0:
      if sigy[-1] == 0:
         zero_values += 1
   else:
      sy.pop()
      sigy.pop()
      sigyerr.pop()
if len(sx) < 2 or len(sy) < 2:
   print("<tr><td colspan=\"5\" align=\"center\">")
   print("<font color=\"red\">")
   print("Insufficient data, please add at least 2 valid measurements with errors and try again!")
   print("</font></td></tr>")
elif zero_values == 0 and breaking_bad == 0:
   if "fit" in form:
      fit_and_plot(sx, sigx, sigxerr, sy, sigy, sigyerr)
else:
   print("<tr><td colspan=\"5\" align=\"center\">")
   print("<font color=\"red\">")
   print("Invalid data, please correct errors in the above data and try again!")
   print("</font></td></tr>")

print_tail()
