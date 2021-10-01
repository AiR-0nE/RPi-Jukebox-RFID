import React, { forwardRef } from 'react';
import { Link } from 'react-router-dom';
import { isNil, reject } from 'ramda';

import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  makeStyles,
  Typography,
} from '@material-ui/core';

import BookmarkIcon from '@material-ui/icons/Bookmark';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  }
}));

const CardsList = ({ cardsList }) => {
  const classes = useStyles();

  const ListItemLink = (cardId) => {
    const EditCardLink = forwardRef((props, ref) => {
      const { data } = props;
      const location = {
        pathname: `/cards/${data.id}/edit`,
        state: data,
      };

      return <Link ref={ref} to={location} {...props} />
    });

    const description = cardsList[cardId].from_quick_select
      ? reject(
          isNil,
          [cardsList[cardId].from_quick_select, cardsList[cardId].action.args]
        ).join(', ')
      : cardsList[cardId].func

    return (
      <ListItem
        button
        component={EditCardLink}
        data={{ id: cardId, ...cardsList[cardId] }}
        key={cardId}
      >
        <ListItemAvatar>
          <Avatar>
            <BookmarkIcon />
          </Avatar>
        </ListItemAvatar>
        <ListItemText
          primary={cardId}
          secondary={description}
        />
      </ListItem>
    );
  }

  return (
    cardsList && Object.keys(cardsList).length > 0
      ? <List className={classes.root}>
          {Object.keys(cardsList).map(ListItemLink)}
        </List>
      : <Typography>No cards registered!</Typography>
  );
}

export default React.memo(CardsList);