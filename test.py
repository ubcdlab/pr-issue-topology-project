import re

test = '''
 I don't know If I misunderstood but after https://github.com/jekyll/jekyll-admin/pull/31, it just works properly without setting headers. As I tried to mean it in my comment here grin

    Thank you, Ben. This PR works great.

Sorry If I couldn't express that. I said still no work for just setting Origin before merging https://github.com/jekyll/jekyll-admin/pull/31. If that's not the case, do you want me to reproduce the issue before https://github.com/jekyll/jekyll-admin/pull/31? Now I have to set the flag to production in order to do that as I merged my branch with master.
'''
test2 = '''
> I don't have the write access to master branch and thus can't merge it

@rush-skills my fault, once again. I misconfigured the repo. You should be able to merge now.

> Would it be good if we merge jekyll and admin folders into jekyll_admin or something else?

It's a strange Rubyism that prefers explicit namespaces. I actually [suggested the opposite originally](https://github.com/jekyll/gsoc/pull/1#issuecomment-221260886) and then corrected myself. In Ruby, `jekyll_admin` would be `/lib/jekyll_admin/` and JekyllAdmin while `jekyll-admin` would be `/lib/jekyll/admin` and `Jekyll::Admin`. I think the second is preferable, to namespace this within Jekyll, rather than within its own top-level `JekyllAdmin` namespace. It's mostly semantics, but may make referencing Jekyll objects _slightly_ easier.

also, in #1
'''


result = re.findall('\/jekyll\/jekyll-admin\/(issues|pull)+\/(\d)+', test)
result2 = re.search('\/jekyll\/jekyll-admin\/(issues|pull)+\/(\d)+', test)

result3 = [x.group(1) for x in re.finditer('(?:\/jekyll\/jekyll-admin\/)(?:issues|pull)+\/(\d+)', test)]
result4 = re.findall('(?<=#)1', test2)

# print(result)
# print(result2.group())
print(result3)
print(result4)