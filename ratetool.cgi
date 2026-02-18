#!/usr/bin/perl
#
# ratetool.cgi - cgi script for running the Hall D coherent bremsstrahlung
#                rates calculator, a paw tool written by R.T.Jones.
#

use CGI;

our $q = new CGI;

# set the run parameters

sub setParameter
{
   my ($par,$desc,$default,$unit) = @_;
   if (!defined $q->param($par) || $q->param("default $par")) {
      $q->delete("default $par");
      $q->param($par,$default);
   }
   return "<tr><td>$desc\n".
          $q->textfield(-name=>$par,-size=>5,
                        -value=>$q->param($par))."$unit\n".
          $q->submit(-name=>"default $par",-value=>'default').
          "</td></tr>\n";
}

# start a vnc server to handle X11 graphics

sub startX11
{
   $ENV{'HOME'} = "/home/www";
   system "vncserver :99 >/dev/null 2>&1";
}

# main execution starts here

if (defined $q->param('run')) {
   startX11();
   my $datafile = "run_$$.macro";
   open(OUT,">work/$datafile") || die;
   print OUT
      "option nbox\n",
      "option zfl1\n",
      "gr/set pass 3\n",
      "gr/set cshi 0.02\n",
      "gr/set xmgl 3\n",
      "gr/set xmgr 1\n",
      "gr/set xlab 2\n",
      "size 16 16\n",
      "opt utit\n",
      "exec cobrems id=100",
      "             nbins=",$q->param("photonNbins"),
      "             Emin=",$q->param("photonEmin"),
      "             Emax=",$q->param("photonEmax"),
      "             E0=",$q->param("beamEnergy"),
      "             Epeak=",$q->param("photonEpeak"),
      "             ytilt=",$q->param("radSecondTilt"),
      "             emit=",$q->param("beamEmittance"),
      "             epol=",$q->param("beamCircPolar"),
      "             dist=",$q->param("collimDistance"),
      "             mos=",$q->param("mosaicSpread"),
      "             coldiam=0.1",
      "             radt=",$q->param("radThickness"),
      "             cur=",$q->param("beamCurrent"),
      "             pElim0=",$q->param("peakElow"),
      "             pElim1=",$q->param("peakEhigh"),
      "             bElim0=",$q->param("backElow"),
      "             bElim1=",$q->param("backEhigh"),
      "             eElim0=",$q->param("endpElow"),
      "             eElim1=",$q->param("endpEhigh"),
      "\n",
      "exec cobrems id=200",
      "             nbins=",$q->param("photonNbins"),
      "             Emin=",$q->param("photonEmin"),
      "             Emax=",$q->param("photonEmax"),
      "             E0=",$q->param("beamEnergy"),
      "             Epeak=",$q->param("photonEpeak"),
      "             ytilt=",$q->param("radSecondTilt"),
      "             emit=",$q->param("beamEmittance"),
      "             epol=",$q->param("beamCircPolar"),
      "             dist=",$q->param("collimDistance"),
      "             mos=",$q->param("mosaicSpread"),
      "             coldiam=",$q->param("collimDiam"),
      "             radt=",$q->param("radThickness"),
      "             cur=",$q->param("beamCurrent"),
      "             pol=1",
      "             coh=1",
      "             pElim0=",$q->param("peakElow"),
      "             pElim1=",$q->param("peakEhigh"),
      "             bElim0=",$q->param("backElow"),
      "             bElim1=",$q->param("backEhigh"),
      "             eElim0=",$q->param("endpElow"),
      "             eElim1=",$q->param("endpEhigh"),
      "\n",
      "exec cobrems id=250",
      "             nbins=",$q->param("photonNbins"),
      "             Emin=",$q->param("photonEmin"),
      "             Emax=",$q->param("photonEmax"),
      "             E0=",$q->param("beamEnergy"),
      "             Epeak=",$q->param("photonEpeak"),
      "             ytilt=",$q->param("radSecondTilt"),
      "             emit=",$q->param("beamEmittance"),
      "             epol=",$q->param("beamCircPolar"),
      "             dist=",$q->param("collimDistance"),
      "             mos=",$q->param("mosaicSpread"),
      "             coldiam=",$q->param("collimDiam"),
      "             radt=",$q->param("radThickness"),
      "             cur=",$q->param("beamCurrent"),
      "             pol=2",
      "             pElim0=",$q->param("peakElow"),
      "             pElim1=",$q->param("peakEhigh"),
      "             bElim0=",$q->param("backElow"),
      "             bElim1=",$q->param("backEhigh"),
      "             eElim0=",$q->param("endpElow"),
      "             eElim1=",$q->param("endpEhigh"),
      "\n",
      "exec cobrems id=300",
      "             nbins=",$q->param("photonNbins"),
      "             Emin=",$q->param("photonEmin"),
      "             Emax=",$q->param("photonEmax"),
      "             E0=",$q->param("beamEnergy"),
      "             Epeak=",$q->param("photonEpeak"),
      "             ytilt=",$q->param("radSecondTilt"),
      "             emit=",$q->param("beamEmittance"),
      "             epol=",$q->param("beamCircPolar"),
      "             dist=",$q->param("collimDistance"),
      "             mos=",$q->param("mosaicSpread"),
      "             coldiam=",$q->param("collimDiam"),
      "             radt=",$q->param("radThickness"),
      "             cur=",$q->param("beamCurrent"),
      "             pElim0=",$q->param("peakElow"),
      "             pElim1=",$q->param("peakEhigh"),
      "             bElim0=",$q->param("backElow"),
      "             bElim1=",$q->param("backEhigh"),
      "             eElim0=",$q->param("endpElow"),
      "             eElim1=",$q->param("endpEhigh"),
      "\n",
      "atit 'E[g] (GeV)' 'collimated beam rate (/GeV/s)'\n",
      "pict/print rate_$$.gif\n",
      "div 200 300 400\n",
      "h/pl 400 c\n",
      "atit 'E[g] (GeV)' 'linear polarization'\n",
      "pict/print linpolar_$$.gif\n",
      "div 250 300 450\n",
      "h/pl 450 c\n",
      "atit 'E[g] (GeV)' 'circular polarization'\n",
      "pict/print circpolar_$$.gif\n",
      "div 300 100 500\n",
      "h/pl 500 c\n",
      "atit 'E[g] (GeV)' 'tagging efficiency'\n",
      "pict/print tageff_$$.gif\n",
      "h/file 25 cobrems_$$.hbook ! n\n",
      "hrout 0\n",
      "close 25\n",
      "exit\n";
   close(OUT);
   $shcmd = ". /etc/profile.d/cern.sh;" .
            "cd work; " .
            "DISPLAY=:99.0 pawX11 -w 1 < $datafile;" .
            "h2root cobrems_$$.hbook";
   open(OUT,"$shcmd |") || die;
   @polar_sums = ();
   @outlog = ();
   while (<OUT>) {
      push(@outlog,$_);
      if (/tagged sum is/) {
         my @sum = split(' ', $_);
         push(@polar_sums,$sum[-1]);
      }
      $tagged_sum = $_ if (/tagged sum is/);
      $bg_sum = $_ if (/bg sum is/);
      $endpoint_sum = $_ if (/endpoint sum is/);
      $beam_power = $_ if (/beam power is/);
      $tagged_sum =~ s/tagged sum/primary peak sum/;
      $bg_sum =~ s/bg sum/low-energy flux sum/;
      $endpoint_sum =~ s/endpoint sum/high-energy sum/;
      $beam_power =~ s/beam power/beam power/;
   }
   close(OUT);
   open(LOG,">/tmp/ratetool.log") || die;
   print LOG @outlog;
   close(LOG);
}

print $q->header(),
      $q->start_html(-title=>'Hall D Coherent Bremsstrahlung Rate Calculator'),
      $q->start_form(-method=>'get',-enctype=>&CGI::URL_ENCODED),
      "<p align=\"center\">\n",
      "<table>\n",
      "<tr><td colspan=\"2\">\n",
      "<h2 align=\"center\">Hall D Coherent Bremsstrahlung Rate Calculator</h2>\n",
      "<p align=\"center\">Richard Jones, University of Connecticut<br>\n",
      "August 12, 2012</p>\n",
      "</td></tr>\n",
      "<tr><td align=\"center\" colspan=\"2\">\n",
      $q->submit(-name=>'submit',-value=>'update'),
      "</td></tr>\n",
      "<tr valign=\"top\"><td width=\"500\">\n",
      "<table>\n",
      setParameter("beamEnergy","Electron beam energy",12.,"GeV"),
      setParameter("beamCurrent","Electron beam current",2.2,"µA"),
      setParameter("beamEmittance","Electron beam emmitance",2.5e-9,"m"),
      setParameter("beamCircPolar","Electron beam circular polarization",0,""),
      setParameter("radThickness","Radiator thickness",20e-6,"m"),
      setParameter("mosaicSpread","Radiator mosaic spread",20e-6,"rad"),
      setParameter("radSecondTilt","Radiator secondary tilt",250e-3,"rad"),
      setParameter("photonEpeak","Photon spectrum peak energy",9.,"GeV"),
      setParameter("photonNbins","Number of bins in photon spectrum",200,""),
      setParameter("photonEmax","Photon spectrum energy maximum",12.,"GeV"),
      setParameter("photonEmin","Photon spectrum energy minimum",0.,"GeV"),
      setParameter("collimDistance","Radiator-collimator distance",75.,"m"),
      setParameter("collimDiam","Collimator diameter",3.4e-3,"m"),
      "</table>\n",
      "</td><td width=\"500\">\n",
      "<table>\n",
      setParameter("peakElow","Low edge of primary peak window",8.4,"GeV"),
      setParameter("peakEhigh","High edge of primary peak window",9.0,"GeV"),
      setParameter("backElow","Low edge of background window",0.1,"GeV"),
      setParameter("backEhigh","High edge of background window",3.0,"GeV"),
      setParameter("endpElow","Low edge of endpoint tagging window",10.7,"GeV"),
      setParameter("endpEhigh","High edge of endpoint tagging window",11.7,"GeV");
      if (defined $tagged_sum) {
         $tagged_sum =~ s/primary/Primary/;
         print "<tr><td>&nbsp;</td></tr>",
               "<tr><td><b>$tagged_sum </b></td></tr>\n";
      }
      if ((@polar_sums) and @polar_sums > 2) {
         $polar_mean = sprintf("%.5f", $polar_sums[1]/($polar_sums[3]+1e-99));
         print "<tr><td><b>Average peak polarization $polar_mean</b>",
               "</td></tr>\n";
      }
      if (defined $bg_sum) {
         $bg_sum =~ s/low-energy/Background/;
         print "<tr><td><b>$bg_sum </b></td></tr>\n";
      }
      if (defined $endpoint_sum) {
         $endpoint_sum =~ s/high-energy/Endpoint tagged/;
         print "<tr><td><b>$endpoint_sum </b></td></tr>\n";
      }
      if (defined $beam_power) {
         $beam_power =~ s/beam power/Total beam power\/W/;
         print "<tr><td><b>$beam_power </b></td></tr>\n";
      }
      else {
         $beam_power = "Total beam power\/W: 0";
         print "<tr><td><b>$beam_power </b></td></tr>\n";
      }

print "</table>\n",
      "</td></tr>\n",
      "<tr height=\"50\"><td align=\"center\" colspan=\"2\">\n",
      $q->submit(-name=>'run',-value=>'plot collimated beam rate spectrum'),
      "</td></tr>\n";

      if (-r "work/rate_$$.gif") {
         print
         "<tr><td align=\"center\" colspan=\"2\">\n",
         "<img src=\"work/rate_$$.gif\">\n",
         "</td></tr>";
      }
      if (-r "work/linpolar_$$.gif") {
         print
         "<tr><td align=\"center\" colspan=\"2\">\n",
         "<img src=\"work/linpolar_$$.gif\">\n",
         "</td></tr>";
      }
      if (-r "work/tageff_$$.gif") {
         print
         "<tr><td align=\"center\" colspan=\"2\">\n",
         "<img src=\"work/tageff_$$.gif\">\n",
         "</td></tr>";
      }
      if (-r "work/circpolar_$$.gif") {
         print
         "<tr><td align=\"center\" colspan=\"2\">\n",
         "<img src=\"work/circpolar_$$.gif\">\n",
         "</td></tr>";
      }
      if (-r "work/cobrems_$$.root") {
         print
         "<tr><td align=\"center\" colspan=\"2\">\n",
         "<a href=\"work/cobrems_$$.root\">",
         "ROOT file containing the above histograms</a>",
         "</td></tr>";
      }
      print
      "</table>\n",
      $q->end_form;
      $q->end_html();
