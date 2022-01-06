from functools import wraps
from telebot import TeleBot, logger, apihelper


def add_method(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        setattr(cls, func.__name__, wrapper)

        return func  # returning func means func can still be used normally

    return decorator


@add_method(TeleBot)  # adding a method for cyclic functions to work correctly
def process_new_updates(self, updates):
    upd_count = len(updates)
    logger.debug('Received {0} new updates'.format(upd_count))
    if upd_count == 0:
        self.process_cyclic_actions([None])
        return

    new_messages = None
    new_edited_messages = None
    new_channel_posts = None
    new_edited_channel_posts = None
    new_inline_queries = None
    new_chosen_inline_results = None
    new_callback_queries = None
    new_shipping_queries = None
    new_pre_checkout_queries = None
    new_polls = None
    new_poll_answers = None
    new_my_chat_members = None
    new_chat_members = None
    chat_join_request = None

    for update in updates:
        if apihelper.ENABLE_MIDDLEWARE:
            try:
                self.process_middlewares(update)
            except Exception as e:
                logger.error(str(e))
                if not self.suppress_middleware_excepions:
                    raise
                else:
                    if update.update_id > self.last_update_id:
                        self.last_update_id = update.update_id
                    continue

        if update.update_id > self.last_update_id:
            self.last_update_id = update.update_id
        if update.message:
            if new_messages is None:
                new_messages = []
            new_messages.append(update.message)
        if update.edited_message:
            if new_edited_messages is None:
                new_edited_messages = []
            new_edited_messages.append(update.edited_message)
        if update.channel_post:
            if new_channel_posts is None:
                new_channel_posts = []
            new_channel_posts.append(update.channel_post)
        if update.edited_channel_post:
            if new_edited_channel_posts is None:
                new_edited_channel_posts = []
            new_edited_channel_posts.append(update.edited_channel_post)
        if update.inline_query:
            if new_inline_queries is None:
                new_inline_queries = []
            new_inline_queries.append(update.inline_query)
        if update.chosen_inline_result:
            if new_chosen_inline_results is None:
                new_chosen_inline_results = []
            new_chosen_inline_results.append(update.chosen_inline_result)
        if update.callback_query:
            if new_callback_queries is None:
                new_callback_queries = []
            new_callback_queries.append(update.callback_query)
        if update.shipping_query:
            if new_shipping_queries is None:
                new_shipping_queries = []
            new_shipping_queries.append(update.shipping_query)
        if update.pre_checkout_query:
            if new_pre_checkout_queries is None:
                new_pre_checkout_queries = []
            new_pre_checkout_queries.append(update.pre_checkout_query)
        if update.poll:
            if new_polls is None:
                new_polls = []
            new_polls.append(update.poll)
        if update.poll_answer:
            if new_poll_answers is None:
                new_poll_answers = []
            new_poll_answers.append(update.poll_answer)
        if update.my_chat_member:
            if new_my_chat_members is None:
                new_my_chat_members = []
            new_my_chat_members.append(update.my_chat_member)
        if update.chat_member:
            if new_chat_members is None:
                new_chat_members = []
            new_chat_members.append(update.chat_member)
        if update.chat_join_request:
            if chat_join_request is None:
                chat_join_request = []
            chat_join_request.append(update.chat_join_request)

    if new_messages:
        self.process_new_messages(new_messages)
    if new_edited_messages:
        self.process_new_edited_messages(new_edited_messages)
    if new_channel_posts:
        self.process_new_channel_posts(new_channel_posts)
    if new_edited_channel_posts:
        self.process_new_edited_channel_posts(new_edited_channel_posts)
    if new_inline_queries:
        self.process_new_inline_query(new_inline_queries)
    if new_chosen_inline_results:
        self.process_new_chosen_inline_query(new_chosen_inline_results)
    if new_callback_queries:
        self.process_new_callback_query(new_callback_queries)
    if new_shipping_queries:
        self.process_new_shipping_query(new_shipping_queries)
    if new_pre_checkout_queries:
        self.process_new_pre_checkout_query(new_pre_checkout_queries)
    if new_polls:
        self.process_new_poll(new_polls)
    if new_poll_answers:
        self.process_new_poll_answer(new_poll_answers)
    if new_my_chat_members:
        self.process_new_my_chat_member(new_my_chat_members)
    if new_chat_members:
        self.process_new_chat_member(new_chat_members)
    if chat_join_request:
        self.process_new_chat_join_request(chat_join_request)
    self.process_cyclic_actions([None])


@add_method(TeleBot)  # adding a method for cyclic functions to work correctly
def process_cyclic_actions(self, new_messages):
    self._notify_command_handlers(self.cyclic_actions, new_messages)


@add_method(TeleBot)  # adding a method for cyclic functions to work correctly
def cyclic_actions_handler(self):
    def decorator(handler):
        handler_dict = self._build_handler_dict(handler,
                                                chat_types=None,
                                                content_types=None,
                                                commands=None,
                                                regexp=None,
                                                func=None)
        self.add_cyclic_actions_handler(handler_dict)
        return handler

    return decorator


@add_method(TeleBot)  # adding a method for cyclic functions to work correctly
def add_cyclic_actions_handler(self, handler_dict):
    self.cyclic_actions.append(handler_dict)
