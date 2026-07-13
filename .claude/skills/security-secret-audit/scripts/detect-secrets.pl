use strict;
use warnings;

my $label = 'input';
my $path = '';

while (@ARGV) {
    my $arg = shift @ARGV;
    if ($arg eq '--label') {
        die "missing value for --label\n" unless @ARGV;
        $label = shift @ARGV;
    }
    elsif ($arg eq '--path') {
        die "missing value for --path\n" unless @ARGV;
        $path = shift @ARGV;
    }
    else {
        die "unknown option: $arg\n";
    }
}

sub is_placeholder {
    my ($value) = @_;

    return 1 if $value eq '' || $value =~ /^\*+$/;
    return 1 if $value =~ /^(?:null|none|undefined|true|false)$/i;
    return 1 if $value =~ /^(?:your|replace|changeme|dummy|example|test|placeholder|redacted|not[-_]?set)(?:[-_].*)?$/i;
    return 1 if $value =~ /(?:^|[-_])(?:your|replace|example|fake|mock|placeholder|actual[-_]?key|x{4,})(?:[-_]|$)/i;
    return 1 if $value =~ /^sk-(?:proj-)?(?:x|-)+$/i;
    return 1 if $value =~ /^(?:\$\{?|\{\{|<|process\.env\b|os\.(?:environ|getenv)\b|getenv\b|config\.|settings\.|env\.)/i;
    return 1 if $value =~ /^[A-Z][A-Z0-9_]{2,}$/;

    return 0;
}

sub is_config_like_path {
    return 1 if $path eq '';

    my ($name) = $path =~ m{([^/]+)$};
    return 1 if $name =~ /^\.env(?:\..+)?$/i;
    return 1 if $name =~ /\.(?:json|ya?ml|toml|ini|cfg|conf|properties)$/i;
    return 1 if $name =~ /(?:secret|credential|config|settings)/i;

    return 0;
}

my $secret_suffix = qr/(?:api[_-]?key|secret|password|passwd|private[_-]?key|access[_-]?key|client[_-]?secret)/i;
my $secret_name = qr/
    (?:
        (?:$secret_suffix|[A-Za-z_][A-Za-z0-9_-]*$secret_suffix)[A-Za-z0-9_-]*
      |
        (?:token|[A-Za-z_][A-Za-z0-9_-]*(?:auth|access|refresh|session|bearer|github|gitlab|slack|npm|stripe)[_-]?token)
    )
/ix;

my $found = 0;
my $line_number = 0;

while (my $line = <STDIN>) {
    ++$line_number;
    last if index($line, "\0") >= 0;

    my @rules;

    push @rules, 'private-key-material'
        if $line =~ /-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----/;
    if ($line =~ /\b(sk-[A-Za-z0-9_-]{16,})\b/ && !is_placeholder($1)) {
        push @rules, 'openai-style-api-key';
    }
    if ($line =~ /\b(gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{22,})\b/ && !is_placeholder($1)) {
        push @rules, 'github-token';
    }
    push @rules, 'aws-access-key-id'
        if $line =~ /\bAKIA[0-9A-Z]{16}\b/;
    push @rules, 'google-api-key'
        if $line =~ /\bAIza[0-9A-Za-z_-]{35}\b/;
    if ($line =~ /\b(xox(?:b|p|a|r|s)-[0-9A-Za-z-]{10,})\b/ && !is_placeholder($1)) {
        push @rules, 'slack-token';
    }
    if ($line =~ /\b(glpat-[0-9A-Za-z_-]{20,})\b/ && !is_placeholder($1)) {
        push @rules, 'gitlab-token';
    }
    if ($line =~ /\b(npm_[A-Za-z0-9]{36})\b/ && !is_placeholder($1)) {
        push @rules, 'npm-token';
    }
    if ($line =~ /\b((?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,})\b/ && !is_placeholder($1)) {
        push @rules, 'stripe-secret-key';
    }
    push @rules, 'json-web-token'
        if $line =~ /\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/;

    if (is_config_like_path() && $line =~ /\b($secret_name)\b\s*[:=]\s*(?:"([^"]*)"|'([^']*)'|([^\s,;\}\]\)#]+))/) {
        my $value = defined $2 ? $2 : defined $3 ? $3 : $4;
        push @rules, 'named-secret-literal'
            if length($value) >= 16 && !is_placeholder($value);
    }

    my %seen;
    for my $rule (@rules) {
        next if $seen{$rule}++;
        print "$label:$line_number:$rule\n";
        $found = 1;
    }
}

exit($found ? 2 : 0);
