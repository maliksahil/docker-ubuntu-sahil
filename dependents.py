#!/usr/bin/python3
#
# usage: python3 docker_descendants.py <image_id> ...

import sys
from subprocess import check_output


def main(images):
    image_ids = set(images)
    all_images = docker_images('--all', '--quiet')
    all_links = parse_links(docker_links(all_images))
    descendants = desc(image_ids, all_links)
    pred = lambda s: lambda line: s[:12] in line
    match = list(map(pred, descendants))
    return filter(lambda i: any(s(i) for s in match), docker_images())


def parse_links(lines):
    parseid = lambda s: s.replace('sha256:', '')
    for line in reversed(list(lines)):
        yield list(map(parseid, line.split()))


def desc(image_ids, links):
    if links:
        link, *tail = links
        if len(link) > 1:
            image_id, parent_id = link
            checkid = lambda i: parent_id.startswith(i)
            if any(map(checkid, image_ids)):
                return desc(image_ids | {image_id}, tail)
        return desc(image_ids, tail)
    return image_ids


def docker_links(images):
    cmd = [ 'docker', 'inspect', '--format={{.Id}} {{.Parent}}']
    return run(cmd + images)


def docker_images(*args):
    return run(('docker', 'images') + args)


def run(cmd):
    return check_output(cmd, universal_newlines=True).splitlines()


if __name__ == '__main__':
    print('\n'.join(main(sys.argv[1:])))