#!/usr/bin/perl -wT

use DBI;
use CGI;
use Template;

use vars qw( $db_host $db_name $db_user $db_pass );
require "/etc/bzorg_vendordb.conf";

my $cgi = new CGI;

my $dsn = "DBI:mysql:host=$db_host;database=$db_name";
my $dbh = DBI->connect($dsn, $db_user, $db_pass, {
    RaiseError => 1,
    AutoCommit => 1,
    ShowErrorStatement => 1,
    TaintIn => 1,
    FetchHashKeyName => 'NAME_lc',
});

my $regions = $dbh->selectcol_arrayref(
    "SELECT DISTINCT region FROM vendors ORDER BY region");

my $vendors = $dbh->selectall_arrayref(
    "SELECT name, website, services, location, willwork, 
            contact, comment, region, contributor 
       FROM vendors WHERE approved = 1
   ORDER BY contributor DESC, RAND()", {Slice=>{}});

print $cgi->header('text/javascript');
my $template = new Template({
  PRE_CHOMP => 1,
  FILTERS   => {
      js => sub {
          my ($var) = @_;
          $var =~ s/([\\\'\"\/])/\\$1/g;
          $var =~ s/\n/\\n/g;
          $var =~ s/\r/\\r/g;
          $var =~ s/\@/\\x40/g; # anti-spam for email addresses
          return $var;
      },
  },
});
$template->process('bz_vendors.tmpl', {
    regions => $regions,
    vendors => $vendors,
}) || die $template->error;
