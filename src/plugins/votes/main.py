from pluginsdk import PluginInterface

class VotePlugin(PluginInterface):
    def event_load(self):
        self.options = []
        self.votes = {}
        self.voted = []
        self.prefix_new = ""

        self.log(self.LINFO, "Voting plugin is ready")

    def _check_if_auth(self, m, required):
        if (m.author.isChatModerator or m.author.isChatOwner) and required == "mod":
            # All moderators can preform
            return True
        elif m.author.isChatOwner and required == "owner":
            # Only the owner can preform
            return True
        elif required == "all":
            # All users can preform
            return True
        else:
            return False
    
    def _handle_vote_end(self,m):
        if not self._check_if_auth(m, self.delete_poll_perms):  # Ensure user can end a vote
            return

        winning_vote = max(self.votes, key=self.votes.get)
        self.log(self.LINFO, f"Winning vote: {winning_vote}")
        self.gui_update.emit(f"Winning vote: {winning_vote}")

        self.options = None
        self.votes = None
        self.voted = None

    def _handle_vote_create(self, m):
        if not self._check_if_auth(m, self.create_poll_perms):  # Ensure user can create a vote
            return

        self.log(self.LINFO, "Creating vote...")
        options = m.message.replace(f"{self.prefix_new} ", "", 1)  # Formatting
        options = options.split(self.option_delim)  # Split each option

        self.options = options
        self.votes = {option: 0 for option in self.options}

    def _handle_vote_req(self, m):
        if self.options == None or self.votes == None:
            # There's no active vote!
            self.log(self.LINFO, "No active vote!")
            return
        
        if not self._check_if_auth(m, self.cast_vote_perms):  # Ensure user can vote
            return

        self.log(self.LINFO, "Person voted!")
        vote = m.message.replace(f"{self.prefix_vote} ", "", 1)
        
        if m.author.channelId in self.voted:
            self.log(self.LINFO, "Person tried to vote twice!")
            return
        else:
            try:
                self.votes[vote] += 1
                self.voted.append(m.author.channelId)
            except KeyError:
                self.log(self.LINFO, "Well that errored, they probably typed it in wrong, just gonna ignore it")
    
    def event_message(self, m):
        # self.log(self.LINFO, self.options, self.votes)
        if m.message.startswith(f"{self.prefix_new}"):
            if self._check_if_auth(m, self.create_poll_perms):
                self._handle_vote_create(m)
            else:
                self.log(self.LINFO, "User tried to create a poll who cannot do so")

        if m.message.startswith(f"{self.prefix_vote}"):
            self._handle_vote_req(m)
        
        if m.message.startswith(f"!endpoll"):
            self._handle_vote_end(m)

    def event_notify(self, source, data):
        pass

    def configure(self, config):
        self.prefix_new = config["prefix_new"]
        self.prefix_vote = config["prefix_vote"]
        self.option_delim = config["option_delimiter"]
        self.create_poll_perms = config["CREATE_POLL_required_perms"]  # Use "all", "mod" or "owner"
        self.cast_vote_perms = config["VOTE_required_perms"]
        self.delete_poll_perms = config["DELETE_POLL_required_perms"]
    
    def event_main(self, time, loop):
        return

    def event_kill(self):
        pass