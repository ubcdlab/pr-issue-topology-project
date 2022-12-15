from github import Github
import picklereader
import datetime
import sys
import time

class Dataminer(picklereader.PickleReader):
    RATE_LIMIT_THRESHOLD = 100
    EXTRA_RATE_LIMIT_WAIT_DURATION = 5

    def __init__(self, github_token, target_repo_list):
        self.g = Github(github_token)
        self.target_repo_list = target_repo_list

    def download_all_repo_data(self):
        for target_repo in self.target_repo_list:
            self.download_repo_data(target_repo)
    
    def check_rate_limit(self, rate_limit, nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo):
        if rate_limit.core.remaining < self.RATE_LIMIT_THRESHOLD:
            print('Rate limit threshold reached!')
            time_remaining = rate_limit.core.reset - datetime.datetime.utcnow()
            print(f'Rate limit will reset after {time_remaining.seconds // 60} minutes {time_remaining.seconds % 60} seconds')
            print(f'Sleeping for {time_remaining.seconds + self.EXTRA_RATE_LIMIT_WAIT_DURATION} seconds.')
            self.write_variables_to_file(nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo)
            time.sleep(time_remaining.seconds + self.EXTRA_RATE_LIMIT_WAIT_DURATION)

    def download_repo_data(self, target_repo):
        repo = self.g.get_repo(target_repo)
        print(f'Downloading repo: {repo.html_url} with {repo.open_issues} open issues')
        nodes, node_list, comment_list, timeline_list, review_comment_list = self.read_repo_local_file(repo, target_repo)
        
        if (len(nodes) > 0 and len(comment_list) > 0) and len(nodes) == len(comment_list):
            # Already done, just return the results loaded from file
            print('All nodes has already been downloaded and processed. Skipping download.')
            print('To force a re-download, delete the associated .pk pickle files and run the code again.')
            return nodes, comment_list, timeline_list, review_comment_list
        else:
            # Download the remaining nodes
            print(f'Nodes remaining to download from repo: {len(node_list)}')
            try:
                while len(node_list) > 0:
                    self.check_rate_limit(self.g.get_rate_limit(), nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo)
                    issue = node_list[-1] # get the lowest numbered issue we haven't processed
                    node_comments = issue.get_comments()
                    node_timeline = issue.get_timeline()
                    timeline_list.append(list(node_timeline))
                    comment_list.append(list(node_comments))

                    node_list.pop() # remove the issue we just processed from the list
                    print(f'Downloaded node {issue.number}. {len(node_list)} remaining. Rate limit: {self.g.rate_limiting[0]}')
            except Exception as e:
                # This should never happen
                print('To the new RA, an exception has happened, and it\'s not supposed to ever happen.')
                print(e)
                self.write_variables_to_file(nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo)
                sys.exit(1) # abort the download process
            # We made it through downloading the whole thing with no errors, save the full progress
            self.write_variables_to_file(nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo)
            self.g.get_rate_limit() # call the API rate limit check to refresh our rate limit stat
            print(f'Finished downloading entire repo. Rate limit: {self.g.rate_limiting[0]}')
            return nodes, comment_list, timeline_list # return the result
