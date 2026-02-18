#!/usr/bin/python
#
# harptool_2d.py - cgi script for running the Hall D coherent bremsstrahlung
#                  harp scan fitter, a ROOT tool written by R.T.Jones.
#
# This is an updated rewrite of harptool.py that generalizes the model from
# independent X and Y projections into a full 2D phase space treatment.
#
# author: richard.t.jones at uconn.edu
# version: january 1, 2022

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
sigma_collimator = {}

def print_head():
   print("Content-Type: text/html")
   print()
   print("<html>")
   print("<head>")
   print("<title>Hall D Electron Beam Harp Scan 2D Fitting Tool</title>")
   print("</head>")
   print("<body>")
   print("<form action=\"harptool_2d.cgi\" method=\"get\" enctype=\"application/x-www-form-urlencoded\">")
   print("<table>")
   print("<tr><td colspan=\"5\" height=\"150\">")
   print("<h2 align=\"center\">Hall D Electron Beam Harp Scan 2D Fitting Tool</h2>")
   print("<p align=\"center\">Richard Jones, University of Connecticut <br />")
   print("January 1, 2022</p>")
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

def fit_and_plot(sx, sigx, sigxerr, su, sigu, siguerr, sy, sigy, sigyerr):
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

   ufitf = ROOT.TF1("ufitf", fit_model, slimits[0], slimits[1], 3)
   ufitf.SetParameter(0, slimits[1])
   ufitf.SetParameter(1, 1.0)
   xemit = float(html.escape(form.getfirst("emittance_x")))
   yemit = float(html.escape(form.getfirst("emittance_y")))
   ufitf.FixParameter(2, (xemit * yemit)**0.5)
   ufitf.SetLineColor(ROOT.kGreen)
   goodsu = []
   goodsigu = []
   goodsuerr = []
   goodsiguerr = []
   for i in range(len(su)):
      if siguerr[i] < 1:
         goodsu.append(su[i])
         goodsuerr.append(0)
         goodsigu.append(sigu[i])
         goodsiguerr.append(siguerr[i])
   udata = ROOT.TGraphErrors(len(goodsu), numpy.array(goodsu, dtype=float),
                                          numpy.array(goodsigu, dtype=float),
                                          numpy.array(goodsuerr, dtype=float),
                                          numpy.array(goodsiguerr, dtype=float))
   ufit = udata.Fit(ufitf, "qs")
   udata.SetLineColor(ROOT.kBlue)
   udata.SetLineWidth(2)
   udata.SetMarkerColor(ROOT.kGreen)
   udata.SetMarkerStyle(20)

   ss = []
   u0 = []
   u1 = []
   par = [ufit.Parameter(0), ufit.Parameter(1), ufit.Parameter(2)]
   covar = ufit.GetCovarianceMatrix()
   minvar = 0.01**2
   for n in range(0, 101):
      s = slimits[0] + n * (slimits[1] - slimits[0]) / 100
      umu = fit_model([s], par)
      gra = fit_model_gradient([s], par)
      ss.append(s)
      usigma = (covar(0,0) * gra[0]**2 + covar(1,1) * gra[1]**2 +
                2 * covar(0,1) * gra[0] * gra[1] + minvar)**0.5
      u0.append(umu - usigma)
      u1.append(umu + usigma)
      if u0[-1] < 0:
         u0[-1] = 0
   ushade = ROOT.TGraph(2 * len(ss), numpy.array(ss + ss[::-1], dtype=float),
                                     numpy.array(u0 + u1[::-1], dtype=float))
   ushade.SetFillColorAlpha(ROOT.kGreen, 0.2);

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
   xfitf.SetMaximum(max(x1) * 1.2)
   xfitf.Draw()
   xdata.Draw("P")
   xshade.Draw("f")
   scol = float(html.escape(form.getfirst("collimator_spos")))
   sigma_collimator['x'] = xfitf.Eval(scol)
   sigma_collimator['u'] = ufitf.Eval(scol)
   sigma_collimator['y'] = yfitf.Eval(scol)
   gcol = ROOT.TGraph(2, numpy.array([scol] * 2, dtype=float), numpy.array([0, 1.5], dtype=float))
   gcol.Draw("L")
   xspec = ROOT.TArrow(scol, sigma_spec[0], slimits[1], sigma_spec[0], 0.03, "<|")
   xspec.SetAngle(35)
   xspec.Draw()
   c1.Update()
   c1.Print(workdir + "harp-x-" + fitimage)
   c1.Print(workdir + "harp-x-" + str(os.getpid()) + ".pdf")
   ufitf.SetTitle("") # "sigma u vs accelerator s")
   ufitf.GetXaxis().SetTitle("accelerator s coordinate (m)")
   ufitf.GetYaxis().SetTitle("#sigma_{u} (mm)")
   ufitf.SetMinimum(0)
   ufitf.SetMaximum(max(u1) * 1.2)
   ufitf.Draw()
   udata.Draw("P")
   ushade.Draw("f")
   scol = float(html.escape(form.getfirst("collimator_spos")))
   gcol = ROOT.TGraph(2, numpy.array([scol] * 2, dtype=float), numpy.array([0, 1.5], dtype=float))
   gcol.Draw("L")
   uspec = ROOT.TArrow(scol, sigma_spec[0], slimits[1], sigma_spec[0], 0.03, "<|")
   uspec.SetAngle(35)
   uspec.Draw()
   c1.Update()
   c1.Print(workdir + "harp-u-" + fitimage)
   c1.Print(workdir + "harp-u-" + str(os.getpid()) + ".pdf")
   yfitf.SetTitle("") # "sigma y vs accelerator s")
   yfitf.GetXaxis().SetTitle("accelerator s coordinate (m)")
   yfitf.GetYaxis().SetTitle("#sigma_{y} (mm)")
   yfitf.SetMinimum(0)
   yfitf.SetMaximum(max(y1) * 1.2)
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
   print("<div align=\"center\"><img src=\"work/harp-u-" + fitimage + "\"></div>")
   print("<div align=\"center\"><img src=\"work/harp-y-" + fitimage + "\"></div>")
   print("</td></tr>")

def fit_and_plot_2d(sx, sigx, sigxerr, su, sigu, siguerr, sy, sigy, sigyerr):
   c1 = ROOT.TCanvas("c1", "", 600, 600)
   axes = ROOT.TH2D("axes", "", 1, -2, 2, 1, -2, 2)
   axes.GetXaxis().SetTitle("x (mm)")
   axes.GetYaxis().SetTitle("y (mm)")
   axes.GetYaxis().SetTitleOffset(1.2)
   axes.SetStats(0)
   axes.Draw()
   ellipse = []
   for i in range(3):
      if sigu[i] == 999:
         sigu[i] = sigu[0] + ((sigu[1] - sigu[0]) * (su[2] - su[0]) /
                              (su[1] - su[0]))
      tan2alpha = ((sigx[i]**2 + sigy[i]**2 - 2*sigu[i]**2) /
                   (sigx[i]**2 - sigy[i]**2 + 1e-99))
      alpha = numpy.arctan(tan2alpha) / 2
      cos2alpha = numpy.cos(2 * alpha)
      cosalpha = numpy.cos(alpha)
      sinalpha = numpy.sin(alpha)
      A2 = ((sigx[i] * cosalpha)**2 - (sigy[i] * sinalpha)**2) / (2 * cos2alpha)
      B2 = ((sigy[i] * cosalpha)**2 - (sigx[i] * sinalpha)**2) / (2 * cos2alpha)
      ellipse.append(ROOT.TEllipse(0, 0, A2**0.5, B2**0.5, 
                                   0, 360, -alpha * 180/numpy.pi))
      ellipse[-1].SetFillStyle(0)
      ellipse[-1].SetLineColor(1+(i*2+1)%5)
      ellipse[-1].Draw()

   if 'x' in sigma_collimator and 'y' in sigma_collimator and 'u' in sigma_collimator:
      # enforce the triangle inequality between sigma_x, sigma_y, and sigma_u
      #   (sigma_x - sigma_y)**2 < 2 sigma_u**2 < (sigma_x + sigma_y)**2
      sigx = sigma_collimator['x']
      sigy = sigma_collimator['y']
      sigu = sigma_collimator['u']
      while (sigx - sigy)**2 > 2 * sigu**2:
         if sigx > sigy:
            sigx *= 0.95
            sigy *= 1.05
         else:
            sigx *= 1.05
            sigy *= 0.95
      while (sigx + sigy)**2 < 2 * sigu**2:
         sigx *= 1.05
         sigy *= 1.05
         sigu *= 0.95
      tan2alpha = ((sigx**2 + sigy**2 - 2*sigu**2) / (sigx**2 - sigy**2))
      alpha = numpy.arctan(tan2alpha) / 2
      cos2alpha = numpy.cos(2 * alpha)
      cosalpha = numpy.cos(alpha)
      sinalpha = numpy.sin(alpha)
      A2 = ((sigx * cosalpha)**2 -
            (sigy * sinalpha)**2) / (2 * cos2alpha)
      B2 = ((sigy * cosalpha)**2 -
            (sigx * sinalpha)**2) / (2 * cos2alpha)
      ellipse.append(ROOT.TEllipse(0, 0, A2**0.5, B2**0.5,
                                   0, 360, -alpha * 180/numpy.pi))
      ellipse[-1].SetFillStyle(3002)
      ellipse[-1].SetFillColor(6)
      ellipse[-1].SetLineColor(6)
      ellipse[-1].Draw()

   c1.Update()
   c1.Print(workdir + "harp-2d-" + fitimage)
   print("<tr><td colspan=\"5\">")
   print("<div align=\"center\"><img src=\"work/harp-2d-" + fitimage + "\"></div>")
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
set_parameter("harp5C11_usigma", "5C11 harp u sigma", 0, "mm")
print("<td width=\"50\"></td>")
set_parameter("harp5C11_usigma_err", "5C11 harp u sigma error", 0.030, "mm")
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
set_parameter("harp5C11B_usigma", "5C11B harp u sigma", 0, "mm")
print("<td></td>")
set_parameter("harp5C11B_usigma_err", "5C11B harp u sigma error", 0.050, "mm")
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
set_parameter("radHarp_usigma", "radiator harp u sigma", 0, "mm")
print("<td></td>")
set_parameter("radHarp_usigma_err", "radiator harp u sigma error", 0.020, "mm")
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
su = []
sy = []
sigx = []
sigu = []
sigy = []
sigxerr = []
siguerr = []
sigyerr = []
zero_values = 0
breaking_bad = 0
for key in ("harp5C11", "harp5C11B", "radHarp"):
   try:
      sx.append(float(html.escape(form.getfirst(key + "_spos"))))
      su.append(float(html.escape(form.getfirst(key + "_spos"))))
      sy.append(float(html.escape(form.getfirst(key + "_spos"))))
      sigx.append(float(html.escape(form.getfirst(key + "_xsigma"))))
      sigxerr.append(float(html.escape(form.getfirst(key + "_xsigma_err"))))
      sigu.append(float(html.escape(form.getfirst(key + "_usigma"))))
      siguerr.append(float(html.escape(form.getfirst(key + "_usigma_err"))))
      sigy.append(float(html.escape(form.getfirst(key + "_ysigma"))))
      sigyerr.append(float(html.escape(form.getfirst(key + "_ysigma_err"))))
      if key != "radHarp":
         sigu2 = sigx[-1]**2 + sigy[-1]**2 - sigu[-1]**2
         if sigu2 > 0:
            sigu[-1] = sigu2**0.5
         else:
            sigu[-1] = (sigx[-1]**2 + sigy[-1]**2)**0.5 / 30
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
   if siguerr[-1] > 0:
      if sigu[-1] == 0:
         zero_values += 1
   else:
      su.pop()
      sigu.pop()
      siguerr.pop()
   if sigyerr[-1] > 0:
      if sigy[-1] == 0:
         zero_values += 1
   else:
      sy.pop()
      sigy.pop()
      sigyerr.pop()
if len(sx) < 2 or len(su) < 2 or len(sy) < 2:
   print("<tr><td colspan=\"5\" align=\"center\">")
   print("<font color=\"red\">")
   print("Insufficient data, please fill in all 9 inputs with errors and try again!")
   print("</font></td></tr>")
elif zero_values == 0 and breaking_bad == 0:
   if "fit" in form:
      fit_and_plot(sx, [s for s in sigx], [e for e in sigxerr],
                   su, [s for s in sigu], [e for e in siguerr],
                   sy, [s for s in sigy], [e for e in sigyerr])
      fit_and_plot_2d(sx, sigx, sigxerr, su, sigu, siguerr, sy, sigy, sigyerr)
else:
   print("<tr><td colspan=\"5\" align=\"center\">")
   print("<font color=\"red\">")
   print("Invalid data,", breaking_bad, "please correct errors in the above data and try again!")
   print("</font></td></tr>")

print_tail()
