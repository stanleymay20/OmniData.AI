import React, { useCallback, useRef } from 'react';
import { FixedSizeList as List } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';

const ITEM_HEIGHT = 200;
const ITEM_WIDTH = 300;

const GET_DATA_ITEMS = gql`
  query GetDataItems($first: Int!, $after: String) {
    dataItems(first: $first, after: $after) {
      edges {
        node {
          id
          title
          description
          imageUrl
        }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
`;

interface DataItem {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

interface DataFeedProps {
  width?: number;
  height?: number;
}

export const DataFeed: React.FC<DataFeedProps> = ({
  width = ITEM_WIDTH,
  height = ITEM_HEIGHT,
}) => {
  const { data, loading, fetchMore } = useQuery(GET_DATA_ITEMS, {
    variables: { first: 10 },
  });

  const items = data?.dataItems?.edges || [];
  const hasNextPage = data?.dataItems?.pageInfo?.hasNextPage;
  const endCursor = data?.dataItems?.pageInfo?.endCursor;

  const loadMoreItems = useCallback(
    async (startIndex: number, stopIndex: number) => {
      if (!hasNextPage || loading) return;
      
      await fetchMore({
        variables: {
          first: stopIndex - startIndex + 1,
          after: endCursor,
        },
      });
    },
    [fetchMore, hasNextPage, loading, endCursor]
  );

  const isItemLoaded = useCallback(
    (index: number) => !hasNextPage || index < items.length,
    [hasNextPage, items.length]
  );

  const Item = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => {
      if (!isItemLoaded(index)) {
        return (
          <div style={style} className="animate-pulse bg-gray-200 rounded-lg">
            Loading...
          </div>
        );
      }

      const item = items[index]?.node as DataItem;

      return (
        <div
          style={style}
          className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <img
            src={item.imageUrl}
            alt={item.title}
            className="w-full h-32 object-cover rounded-t-lg"
            loading="lazy"
          />
          <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
          <p className="mt-1 text-gray-600">{item.description}</p>
        </div>
      );
    },
    [items, isItemLoaded]
  );

  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={hasNextPage ? items.length + 1 : items.length}
      loadMoreItems={loadMoreItems}
    >
      {({ onItemsRendered, ref }) => (
        <List
          height={window.innerHeight}
          itemCount={hasNextPage ? items.length + 1 : items.length}
          itemSize={ITEM_HEIGHT}
          width={width}
          onItemsRendered={onItemsRendered}
          ref={ref}
        >
          {Item}
        </List>
      )}
    </InfiniteLoader>
  );
}; 