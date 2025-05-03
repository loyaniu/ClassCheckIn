/*
Author: Zhonglin Niu (zn23) and Yuese Li (yl77)
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: { email: v.string(), timestamp: v.number(), name: v.string() },
  handler: async (ctx, args) => {
    const taskId = await ctx.db.insert("checkins", {
      email: args.email,
      timestamp: args.timestamp,
      name: args.name,
    });
    return taskId;
  },
});

// New mutation for manual check-in
export const manualCreate = mutation({
  args: { email: v.string(), name: v.string() },
  handler: async (ctx, args) => {
    const taskId = await ctx.db.insert("checkins", {
      email: args.email,
      timestamp: Math.floor(Date.now() / 1000), // Use current server time in seconds
      name: args.name,
    });
    return taskId;
  },
});

export const retrieve = query({
  args: { email: v.optional(v.string()) },
  handler: async (ctx, args) => {
    if (args.email) {
      // If email is provided, retrieve checkins for that specific email
      return await ctx.db
        .query("checkins")
        .filter(q => q.eq(q.field("email"), args.email))
        .collect();
    } else {
      // If no email is provided, retrieve all checkins
      return await ctx.db.query("checkins").order("desc").collect(); // Order by descending timestamp
    }
  },
});
