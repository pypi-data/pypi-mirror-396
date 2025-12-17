import { useState } from 'react';

import { SORTING_TYPES } from '@routes/constants';


// eslint-disable-next-line import/prefer-default-export
export function useSortTable() {
  const [order, setOrder] = useState(null);
  const [orderBy, setOrderBy] = useState(null);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === SORTING_TYPES.asc;
    setOrder(isAsc ? SORTING_TYPES.desc : SORTING_TYPES.asc);
    setOrderBy(property);
  };

  return {
    order,
    orderBy,
    handleRequestSort,
  };
}
