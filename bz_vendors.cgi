#!/usr/bin/perl -wT

use DBI;
use CGI;
use Template;

use vars qw( $db_host $db_name $db_user $db_pass );
require "/etc/bzorg_vendordb.conf" || die "Couldn't load database config";

my $cgi = new CGI;
my $template = new Template;

my $dbh = DBI->connect("DBI:mysql:host=$db_host;database=$db_name", $db_user, $db_pass)
    || die "Couldn't connect to database\n";

my $sth = $dbh->prepare("SELECT DISTINCT region FROM vendors");
$sth->execute();

my @regionlist = ('All');
while (my ($reg) = $sth->fetchrow_array()) {
  push @regionlist, $reg;
}

my @bindparams = ();

my $region = $cgi->param('region') || 'All';

my $regionpart = "";
if ($region ne 'All') {
  if (!grep { $_ eq $region } @regionlist) {
    print $cgi->header("text/plain");
    print "Invalid region, try again.\n";
    exit;
  }
  $regionpart = 'AND region = ?';
  push @bindparams, $region;
}

$sth = $dbh->prepare("SELECT name, website, services, location, willwork, contact, comment FROM vendors WHERE approved=1 $regionpart ORDER BY RAND()");
$sth->execute(@bindparams);

my %vars = ();
$vars{'vendors'} = [];

while (my $hash = $sth->fetchrow_hashref()) {
  push @{$vars{'vendors'}}, $hash;
};

$vars{'region'} = $region;
$vars{'regionlist'} = \@regionlist;

print $cgi->header("text/html");

$template->process("bz_vendors.tmpl", \%vars)
  || die "Template failed: $@";

