"""Reusable Shopify Admin GraphQL queries and mutations."""

SHOP_INFO_QUERY = """
query GetShopInformation {
  shop {
    name
    email
    myshopifyDomain
    currencyCode
    plan {
      displayName
    }
  }
}
"""

PRODUCTS_QUERY = """
query GetProducts($first: Int = 10, $query: String) {
  products(first: $first, query: $query) {
    edges {
      cursor
      node {
        id
        title
        handle
        status
        totalInventory
        tags
        priceRangeV2 {
          minVariantPrice {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
"""

PRODUCT_CREATE_MUTATION = """
mutation CreateProduct($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      status
      handle
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
"""
