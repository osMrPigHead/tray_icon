function FindProxyForURL(url, host) {
    for (let rule of rules) {
        for (let re of rule[0]) {
            if (host.match(re)) return rule[1]
        }
    }
    return "DIRECT";
}